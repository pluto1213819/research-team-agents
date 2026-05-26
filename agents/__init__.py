"""
ResearchTeam Agents - Agent Implementations
研究员Agent和分析师Agent的实现
"""

import json
import sys
import os
from typing import List, Dict, Any, Optional
from openai import OpenAI

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from communication import MessageBus, Message


class BaseAgent:
    """Agent基类"""

    def __init__(self, name: str, role: str, api_key: str, model: str = "deepseek-chat", api_base: str = "https://api.deepseek.com"):
        self.name = name
        self.role = role
        self.client = OpenAI(api_key=api_key, base_url=api_base)
        self.model = model
        self.bus: Optional[MessageBus] = None
        self.context: List[Dict[str, str]] = []
        self.status = "idle"
    
    def set_bus(self, bus: MessageBus):
        """设置消息总线"""
        self.bus = bus
        self.bus.subscribe(self.name, self._on_message)
    
    def _on_message(self, message: Message):
        """消息回调"""
        self.context.append({
            "role": "user",
            "content": f"[来自 {message.sender}]: {message.content}"
        })
    
    def send_to(self, receiver: str, content: str):
        """发送消息给其他Agent"""
        if self.bus:
            msg = Message(self.name, receiver, content)
            self.bus.send(msg)
    
    def receive_messages(self) -> List[Message]:
        """接收待处理消息"""
        if self.bus:
            return self.bus.receive(self.name)
        return []
    
    def chat(self, prompt: str) -> str:
        """调用LLM"""
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            *self.context[-10:],  # 保留最近10条上下文
            {"role": "user", "content": prompt}
        ]
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7
        )
        
        result = response.choices[0].message.content
        self.context.append({"role": "assistant", "content": result})
        return result
    
    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        raise NotImplementedError


class ResearcherAgent(BaseAgent):
    """研究员Agent - 负责信息收集与调研"""

    def __init__(self, api_key: str, model: str = "deepseek-chat", api_base: str = "https://api.deepseek.com"):
        super().__init__(
            name="研究员小研",
            role="Researcher",
            api_key=api_key,
            model=model,
            api_base=api_base
        )
        self.research_data: List[Dict] = []
    
    def get_system_prompt(self) -> str:
        return """你是"小研"，一位专业的研究分析师。你的职责是：

1. **信息收集**: 围绕研究主题收集相关信息和数据
2. **深度分析**: 从多个角度分析问题
3. **整理归纳**: 将复杂信息整理成清晰的要点

## 工作原则
- 提供准确、有依据的信息
- 注明信息来源和可信度
- 区分事实和推测
- 使用结构化格式呈现发现

请用中文回复，使用Markdown格式组织内容。"""
    
    def research(self, topic: str) -> Dict[str, Any]:
        """执行研究任务"""
        self.status = "researching"
        print(f"  [*] {self.name} 开始研究: {topic}")
        
        # 生成研究问题
        questions_prompt = f"""针对研究主题 "{topic}"，生成5个关键研究问题。
返回JSON格式: {{"questions": ["问题1", "问题2", ...]}}"""
        
        questions_response = self.chat(questions_prompt)
        try:
            questions = json.loads(questions_response)
            if isinstance(questions, dict):
                questions = questions.get("questions", [questions_response])
        except:
            questions = [f"{topic}的核心概念是什么？"]
        
        # 研究每个问题
        findings = []
        for i, question in enumerate(questions[:5], 1):
            print(f"  [>] 研究问题 {i}: {question[:30]}...")
            
            research_prompt = f"""请深入研究以下问题，提供详细的分析和发现：

问题: {question}
主题背景: {topic}

请提供：
1. 关键发现
2. 相关数据或案例
3. 你的分析见解

使用Markdown格式。"""
            
            finding = self.chat(research_prompt)
            findings.append({
                "question": question,
                "answer": finding
            })
        
        # 整理研究报告
        summary_prompt = f"""基于以下研究发现，为主题 "{topic}" 生成一份简洁的研究摘要：

研究发现:
{json.dumps(findings, ensure_ascii=False, indent=2)}

请包含：
1. 核心观点（3-5个）
2. 关键发现
3. 进一步研究建议"""
        
        summary = self.chat(summary_prompt)
        
        result = {
            "topic": topic,
            "questions": questions,
            "findings": findings,
            "summary": summary
        }
        
        self.research_data.append(result)
        self.status = "idle"
        
        # 通知分析师
        if self.bus:
            self.send_to("分析师小析", f"研究完成！主题: {topic}\n\n摘要:\n{summary}")
        
        return result


class AnalystAgent(BaseAgent):
    """分析师Agent - 负责分析与报告生成"""

    def __init__(self, api_key: str, model: str = "deepseek-chat", api_base: str = "https://api.deepseek.com"):
        super().__init__(
            name="分析师小析",
            role="Analyst",
            api_key=api_key,
            model=model,
            api_base=api_base
        )
        self.analysis_results: List[Dict] = []
    
    def get_system_prompt(self) -> str:
        return """你是"小析"，一位资深的数据分析师和报告撰写专家。你的职责是：

1. **数据分析**: 从数据中提取有价值的洞察
2. **趋势识别**: 发现数据中的模式和趋势
3. **报告撰写**: 生成专业、清晰的分析报告
4. **建议提供**: 基于分析提供可行建议

## 工作原则
- 数据驱动，客观分析
- 结论清晰，有理有据
- 使用图表和结构化格式
- 提供可执行的建议

请用中文回复，使用Markdown格式。"""
    
    def analyze(self, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析研究数据并生成报告"""
        self.status = "analyzing"
        print(f"  [==] {self.name} 开始分析研究数据")
        
        topic = research_data.get("topic", "未知主题")
        findings = research_data.get("findings", [])
        summary = research_data.get("summary", "")
        
        # 分析关键洞察
        insight_prompt = f"""基于以下研究数据，提取关键洞察：

主题: {topic}
研究摘要: {summary}

请分析并提供：
1. 3-5个最重要的洞察
2. 每个洞察的重要性说明
3. 潜在的影响或应用"""
        
        insights = self.chat(insight_prompt)
        
        # 生成SWOT分析（如果适用）
        swot_prompt = f"""为以下主题进行简要的SWOT分析：

主题: {topic}
关键发现: {summary[:500]}

返回格式:
- 优势 (Strengths)
- 劣势 (Weaknesses)  
- 机会 (Opportunities)
- 威胁 (Threats)"""
        
        swot = self.chat(swot_prompt)
        
        # 生成建议
        recommendations_prompt = f"""基于以下分析，提供具体的行动建议：

主题: {topic}
洞察: {insights[:500]}

请提供3-5条具体、可执行的建议，每条包含：
- 建议内容
- 预期效果
- 实施难度"""
        
        recommendations = self.chat(recommendations_prompt)
        
        # 生成最终报告
        report = self._generate_report(topic, research_data, insights, swot, recommendations)
        
        result = {
            "topic": topic,
            "insights": insights,
            "swot_analysis": swot,
            "recommendations": recommendations,
            "report": report
        }
        
        self.analysis_results.append(result)
        self.status = "idle"
        
        # 通知研究员
        if self.bus:
            self.send_to("研究员小研", f"分析完成！已生成报告。\n\n建议摘要:\n{recommendations[:300]}...")
        
        return result
    
    def _generate_report(self, topic: str, research_data: Dict, insights: str, swot: str, recommendations: str) -> str:
        """生成最终研究报告"""
        report_prompt = f"""请生成一份专业的研究报告：

# 研究报告: {topic}

## 背景
基于团队研究分析，生成此报告。

## 研究概述
{research_data.get('summary', '')[:500]}

## 关键洞察
{insights[:500]}

## SWOT分析
{swot[:500]}

## 建议
{recommendations[:500]}

请扩展以上内容，生成一份完整、专业的研究报告。使用Markdown格式，包含目录结构。"""
        
        report = self.chat(report_prompt)
        return report

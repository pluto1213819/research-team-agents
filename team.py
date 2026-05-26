"""
ResearchTeam Agents - Team Orchestrator
团队协调器 - 管理多Agent协作
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, Any

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents import ResearcherAgent, AnalystAgent
from communication import MessageBus


class ResearchTeam:
    """研究团队 - 协调多个Agent协作"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini", api_base: str = None):
        # 初始化消息总线
        self.bus = MessageBus()
        
        # 创建Agent团队
        self.researcher = ResearcherAgent(api_key, model, api_base)
        self.analyst = AnalystAgent(api_key, model, api_base)
        
        # 注册到消息总线
        self.researcher.set_bus(self.bus)
        self.analyst.set_bus(self.bus)
        
        # 输出目录
        self.output_dir = os.path.join(os.path.dirname(__file__), "output")
        os.makedirs(self.output_dir, exist_ok=True)
    
    def research_and_analyze(self, topic: str) -> Dict[str, Any]:
        """执行完整的研究分析流程"""
        print(f"\n{'='*60}")
        print(f"  Research Project: {topic}")
        print('='*60)
        
        # 阶段1: 研究
        print(f"\n  Phase 1: Information Collection")
        print("-" * 40)
        research_result = self.researcher.research(topic)
        
        # 阶段2: 分析
        print(f"\n  Phase 2: Analysis & Report")
        print("-" * 40)
        analysis_result = self.analyst.analyze(research_result)
        
        # 阶段3: 保存结果
        print(f"\n  Phase 3: Save Results")
        print("-" * 40)
        saved_files = self._save_results(topic, research_result, analysis_result)
        
        # 显示通信历史
        print(f"\n  Communication Statistics:")
        print(f"   - Total messages: {len(self.bus.message_history)}")
        print(f"   - Researcher sent: {len([m for m in self.bus.message_history if m.sender == 'Researcher'])} messages")
        print(f"   - Analyst sent: {len([m for m in self.bus.message_history if m.sender == 'Analyst'])} messages")
        
        print(f"\n{'='*60}")
        print(f"  Research Complete!")
        print(f"  Results saved to: {self.output_dir}")
        print('='*60)
        
        return {
            "research": research_result,
            "analysis": analysis_result,
            "saved_files": saved_files
        }
    
    def _save_results(self, topic: str, research: Dict, analysis: Dict) -> Dict[str, str]:
        """保存研究结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).strip()[:30]
        
        saved_files = {}
        
        # 保存研究报告
        report_path = os.path.join(self.output_dir, f"report_{safe_topic}_{timestamp}.md")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(analysis.get("report", "Report generation failed"))
        saved_files["report"] = report_path
        print(f"  [Report] {report_path}")
        
        # 保存研究数据
        data_path = os.path.join(self.output_dir, f"data_{safe_topic}_{timestamp}.json")
        with open(data_path, 'w', encoding='utf-8') as f:
            json.dump({
                "topic": topic,
                "timestamp": timestamp,
                "research": research,
                "analysis": {
                    "insights": analysis.get("insights"),
                    "swot": analysis.get("swot_analysis"),
                    "recommendations": analysis.get("recommendations")
                }
            }, f, ensure_ascii=False, indent=2)
        saved_files["data"] = data_path
        print(f"  [Data] {data_path}")
        
        # 保存通信记录
        comm_path = os.path.join(self.output_dir, f"communication_{safe_topic}_{timestamp}.json")
        with open(comm_path, 'w', encoding='utf-8') as f:
            json.dump(self.bus.get_history(), f, ensure_ascii=False, indent=2)
        saved_files["communication"] = comm_path
        print(f"  [Communication] {comm_path}")
        
        return saved_files

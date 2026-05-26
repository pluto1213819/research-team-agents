# ResearchTeam Agents

> 多 Agent 协作研究系统 — 研究员 + 分析师分工合作，自动生成专业研究报告

## 项目简介

ResearchTeam Agents 是一个基于 DeepSeek 大模型的多 Agent 协作系统。用户输入一个研究主题，两个 AI Agent 会自动分工完成信息收集、深度分析、报告撰写全流程，最终输出一份结构化的 Markdown 研究报告。

**核心特点：**

- 两个 Agent 角色分工：研究员负责调研，分析师负责总结报告
- Agent 之间通过消息总线异步通信，模拟真实团队协作
- 自动生成 SWOT 分析、关键洞察、行动建议
- 输出 Markdown 报告 + JSON 结构数据 + 通信日志

## 项目结构

```
research-team-agents/
├── agents/               # Agent 实现
│   └── __init__.py       # 研究员(ResearcherAgent) + 分析师(AnalystAgent)
├── communication/        # 通信系统
│   └── __init__.py       # 消息总线(MessageBus) + 消息对象(Message)
├── output/               # 研究报告输出目录
├── team.py               # 团队协调器，串联研究员和分析师协作
├── main.py               # 主入口文件
├── requirements.txt      # Python 依赖
├── .env.example          # 环境变量配置模板
└── README.md
```

## 工作机制

```
用户输入主题
    │
    ▼
┌──────────────┐    消息     ┌──────────────┐
│  研究员小研   │ ────────▶ │  分析师小析   │
│              │ ◀──────── │              │
│ 生成研究问题  │           │ 提取关键洞察  │
│ 逐题深入调研  │           │ SWOT 分析     │
│ 整理研究摘要  │           │ 生成建议      │
└──────────────┘           └──────┬───────┘
                                  │
                                  ▼
                         ┌────────────────┐
                         │  最终研究报告   │
                         │  (Markdown)    │
                         └────────────────┘
```

**阶段 1 — 信息收集：** 研究员 Agent 围绕主题生成 5 个关键研究问题，逐一调用大模型深入调研，最后整合为研究摘要。

**阶段 2 — 分析报告：** 分析师 Agent 基于研究结果，提取关键洞察、做 SWOT 分析、给出行动建议，最后生成完整的 Markdown 报告。

**阶段 3 — 结果保存：** 报告、结构化数据、通信记录分别写入 `output/` 目录。

## 环境要求

- Python 3.8+
- DeepSeek API Key（[前往获取](https://platform.deepseek.com/)）

## 快速上手

### 1. 安装依赖

```bash
cd research-team-agents
pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
# 复制配置模板
cp .env.example .env

# 编辑 .env，填入你的 DeepSeek API Key
# OPENAI_API_KEY=sk-xxxxxxxx
```

### 3. 运行

```bash
# 演示模式（自动研究一个预设主题）
python main.py --demo

# 直接指定主题
python main.py --topic "2026年量子计算发展前景"

# 交互式菜单
python main.py
```

## 命令行参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--demo` | 运行演示模式 | `python main.py --demo` |
| `--topic "xxx"` | 直接研究指定主题 | `python main.py --topic "新能源趋势"` |
| `--model xxx` | 指定模型（覆盖 .env 配置） | `python main.py --model deepseek-chat` |
| `--api-key xxx` | 指定 API Key（覆盖 .env 配置） | `python main.py --api-key sk-xxx` |

## 输出文件说明

每次研究会生成 3 个文件，保存在 `output/` 目录：

| 文件 | 格式 | 内容 |
|------|------|------|
| `report_*.md` | Markdown | 完整研究报告，含目录、洞察、SWOT、建议 |
| `data_*.json` | JSON | 结构化研究数据，便于二次处理 |
| `communication_*.json` | JSON | Agent 间完整通信记录，用于调试 |

## 配置说明

`.env` 文件支持三个配置项：

```ini
# DeepSeek API Key（必填）
OPENAI_API_KEY=sk-your-api-key

# 模型选择（选填，默认 deepseek-chat）
OPENAI_MODEL=deepseek-chat

# API 地址（选填，默认 DeepSeek 官方地址）
OPENAI_API_BASE=https://api.deepseek.com
```

> 本项目使用 OpenAI 兼容的 API 协议，因此也支持任何兼容 OpenAI 接口的服务（如 DeepSeek、OpenAI、Ollama 等），只需修改 `OPENAI_API_BASE` 和 `OPENAI_MODEL` 即可。

## 常见问题

**Q: 运行时终端中文显示乱码？**

A: Windows 下终端默认使用 GBK 编码，可以加环境变量解决：
```bash
PYTHONIOENCODING=utf-8 python main.py --demo
```
乱码不影响报告生成质量，`output/` 目录下的文件内容正常。

**Q: 支持其他模型吗？**

A: 支持。修改 `.env` 中的 `OPENAI_API_BASE` 和 `OPENAI_MODEL` 即可切换。例如：
- OpenAI: `OPENAI_API_BASE=https://api.openai.com/v1` + `OPENAI_MODEL=gpt-4o-mini`
- Ollama 本地: `OPENAI_API_BASE=http://localhost:11434/v1` + `OPENAI_MODEL=qwen2.5`

**Q: 研究一次需要多长时间？**

A: 取决于主题复杂度和模型响应速度，通常在 30 秒到 2 分钟之间。

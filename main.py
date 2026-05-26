#!/usr/bin/env python3
"""
ResearchTeam Agents - 多Agent协作研究系统
主入口文件

用法:
    python main.py                          # 交互式模式
    python main.py --topic "研究主题"        # 直接研究指定主题
    python main.py --demo                   # 运行演示
"""

import os
import sys
import argparse
from dotenv import load_dotenv

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from team import ResearchTeam


def print_banner():
    """打印欢迎横幅"""
    banner = """
+============================================================+
|              * ResearchTeam Agents                         |
|            多Agent协作研究分析系统                          |
+------------------------------------------------------------+
|  团队成员:                                                 |
|    [研究员小研] - 信息收集与深度调研                        |
|    [分析师小析] - 数据分析与报告撰写                        |
|                                                            |
|  协作模式: 异步消息传递 | 角色分工 | 结果整合               |
+============================================================+
"""
    print(banner)


def run_demo(team: ResearchTeam):
    """运行演示"""
    demo_topic = "2024年人工智能发展趋势"
    print(f"\n>> 演示模式: 研究 '{demo_topic}'")
    print("   (这将展示多Agent协作的完整流程)\n")

    team.research_and_analyze(demo_topic)


def interactive_mode(team: ResearchTeam):
    """交互式模式"""
    print_banner()

    while True:
        try:
            print("\n请选择操作:")
            print("  1. 开始新研究")
            print("  2. 查看历史")
            print("  3. 运行演示")
            print("  4. 退出")

            choice = input("\n请输入选项 (1-4): ").strip()

            if choice == '1':
                topic = input("\n请输入研究主题: ").strip()
                if topic:
                    team.research_and_analyze(topic)
                else:
                    print("[X] 主题不能为空")

            elif choice == '2':
                output_dir = team.output_dir
                if os.path.exists(output_dir):
                    files = os.listdir(output_dir)
                    if files:
                        print(f"\n[*] 历史研究文件 ({output_dir}):")
                        for f in files[-10:]:
                            print(f"   - {f}")
                    else:
                        print("\n[*] 暂无历史记录")
                else:
                    print("\n[*] 暂无历史记录")

            elif choice == '3':
                run_demo(team)

            elif choice == '4':
                print("\n[bye] 再见！感谢使用 ResearchTeam Agents！")
                break

            else:
                print("[X] 无效选项，请重新输入")

        except KeyboardInterrupt:
            print("\n\n[bye] 再见！")
            break
        except Exception as e:
            print(f"\n[X] 错误: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description="ResearchTeam Agents - 多Agent协作研究系统")
    parser.add_argument("--topic", type=str, help="直接研究指定主题")
    parser.add_argument("--demo", action="store_true", help="运行演示模式")
    parser.add_argument("--model", type=str, default=None, help="指定模型")
    parser.add_argument("--api-key", type=str, default=None, help="DeepSeek API Key")

    args = parser.parse_args()

    # 加载环境变量
    load_dotenv()

    # 获取API配置
    api_key = args.api_key or os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("OPENAI_API_BASE", "https://api.deepseek.com")
    model = args.model or os.getenv("OPENAI_MODEL", "deepseek-chat")

    if not api_key:
        print("[X] 错误: 请设置 OPENAI_API_KEY")
        print("   方法1: 设置环境变量 OPENAI_API_KEY")
        print("   方法2: 创建 .env 文件 (参考 .env.example)")
        print("   方法3: 使用 --api-key 参数")
        sys.exit(1)

    # 创建研究团队
    team = ResearchTeam(
        api_key=api_key,
        model=model,
        api_base=api_base
    )

    # 根据参数选择运行模式
    if args.demo:
        run_demo(team)
    elif args.topic:
        team.research_and_analyze(args.topic)
    else:
        interactive_mode(team)


if __name__ == "__main__":
    main()

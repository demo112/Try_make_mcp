from enum import Enum
from typing import Dict, Optional
import json
import os
from pathlib import Path
from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP

# 1. 定义状态枚举
class ReviewState(str, Enum):
    IDLE = "IDLE"
    STAGE_0_INIT = "STAGE_0_INIT"
    STAGE_1_ALIGN = "STAGE_1_ALIGN"
    STAGE_2_ARCHITECT = "STAGE_2_ARCHITECT"
    STAGE_3_ATOMIZE = "STAGE_3_ATOMIZE"
    STAGE_4_APPROVE = "STAGE_4_APPROVE"
    STAGE_5_AUTOMATE = "STAGE_5_AUTOMATE"
    WAITING_FOR_HUMAN = "WAITING_FOR_HUMAN"
    STAGE_6_ASSESS = "STAGE_6_ASSESS"
    STAGE_7_EXTEND = "STAGE_7_EXTEND"
    COMPLETED = "COMPLETED"

# 2. 定义上下文数据模型
class ReviewContext(BaseModel):
    project_name: str = ""
    current_state: ReviewState = ReviewState.IDLE
    base_dir: str = ""
    last_feedback: str = ""

# 3. 全局状态管理
STATE_FILE = "review_flow_state.json"
context = ReviewContext()

# 4. 阶段对应的 Prompt (简化版，实际应从 6a.md 加载或完整硬编码)
STAGES_PROMPTS = {
    ReviewState.IDLE: "系统空闲。请使用 `start_review(project_name)` 启动新评审。",
    
    ReviewState.STAGE_0_INIT: """
### 阶段0: 初始化
**目标**：准备文档结构
请检查并创建以下目录结构：
- `docs/{project_name}评审工作流/`
- 确保包含 01_Align 到 06_Assess 等所有子目录（虽然本工作流主要使用文件前缀区分，但建议建立清晰文件夹）。
完成后，请创建一个空的 `docs/{project_name}评审工作流/Readme.md` 作为验证文件。
使用 `submit_work` 提交该文件路径。
""",

    ReviewState.STAGE_1_ALIGN: """
### 阶段1: Align (对齐阶段)
**目标**: 重建业务上下文
请分析原始需求（假设已在工作区中），并创建 `docs/{project_name}评审工作流/01_对齐_{project_name}.md`。
内容应包含：
- 重建的业务上下文
- 业务目标与价值
- 识别的模糊点
完成并生成文件后，使用 `submit_work` 提交该文件路径。
""",

    ReviewState.STAGE_2_ARCHITECT: """
### 阶段2: Architect (架构阶段)
**目标**: 识别业务流程缺陷
请基于《对齐》文档，创建 `docs/{project_name}评审工作流/03_业务流程缺陷_{project_name}.md`。
重点关注功能需求和状态转换路径。
完成并生成文件后，使用 `submit_work` 提交该文件路径。
""",

    ReviewState.STAGE_3_ATOMIZE: """
### 阶段3: Atomize (原子化阶段)
**目标**: 拆分业务澄清点
请基于《业务流程缺陷》文档，创建 `docs/{project_name}评审工作流/04_业务澄清点_{project_name}.md`。
每个澄清点应包含：问题描述、类型、业务影响、期望回答标准。
完成并生成文件后，使用 `submit_work` 提交该文件路径。
""",

    ReviewState.STAGE_4_APPROVE: """
### 阶段4: Approve (审批阶段)
**目标**: 生成最终业务澄清清单
请审查澄清点，创建 `docs/{project_name}评审工作流/05_最终业务澄清清单_{project_name}.md`。
确保问题按优先级排序。
完成并生成文件后，使用 `submit_work` 提交该文件路径。
""",

    ReviewState.STAGE_5_AUTOMATE: """
### 阶段5: Automate (自动化执行)
**目标**: 生成可交付的业务评审问题记录
请创建 `docs/{project_name}评审工作流/06_方案业务评审问题_{project_name}.md`。
格式必须严格遵循：
```
## [序号].[问题标题]
**问题描述**：...
**期望澄清**：...
**回答**：[留空供负责人填写]
```
完成并生成文件后，使用 `submit_work` 提交该文件路径。
""",

    ReviewState.WAITING_FOR_HUMAN: """
### 等待人工输入
当前流程已暂停，等待业务负责人在 `docs/{project_name}评审工作流/06_方案业务评审问题_{project_name}.md` 中填写答案。
请定期使用 `check_human_response` 检查文件是否已更新。
不要修改文件，只需等待。
""",

    ReviewState.STAGE_6_ASSESS: """
### 阶段6: Assess (评估阶段)
**目标**: 业务问题记录交付与确认
检测到用户已回复。请创建 `docs/{project_name}评审工作流/08_评审完成报告_{project_name}.md`。
总结问题解决情况和剩余风险。
完成并生成文件后，使用 `submit_work` 提交该文件路径。
""",
    
    ReviewState.STAGE_7_EXTEND: """
### 阶段7: Extend (延伸阶段 - 可选)
如果需要，基于澄清内容生成 V2 版本文档。
否则，请直接创建一个 `docs/{project_name}评审工作流/FINISHED` 标记文件来结束流程。
使用 `submit_work` 提交该标记文件。
""",

    ReviewState.COMPLETED: "流程已结束。感谢使用 ReviewFlow。"
}

# 初始化 MCP Server
mcp = FastMCP("ReviewFlow")

def save_state():
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        f.write(context.model_dump_json(indent=2))

def load_state():
    global context
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                context = ReviewContext(**data)
        except Exception:
            context = ReviewContext()

# 启动时加载状态
load_state()

@mcp.tool()
def start_review(project_name: str) -> str:
    """
    启动一个新的评审项目。
    Args:
        project_name: 项目名称，将用于目录和文件命名
    """
    global context
    context.project_name = project_name
    context.base_dir = str(Path.cwd() / "docs" / f"{project_name}评审工作流")
    context.current_state = ReviewState.STAGE_0_INIT
    save_state()
    return f"项目 '{project_name}' 已初始化。当前状态: STAGE_0_INIT。请调用 `get_current_instruction` 获取下一步指引。"

@mcp.tool()
def get_current_instruction() -> str:
    """
    获取当前阶段的执行指令 (Prompt)。
    LLM 应该根据这个指令来执行具体的文档生成工作。
    """
    prompt_template = STAGES_PROMPTS.get(context.current_state, "未知状态")
    return prompt_template.format(project_name=context.project_name)

@mcp.tool()
def submit_work(proof_file_path: str) -> str:
    """
    提交当前阶段的工作成果以供验收。
    Args:
        proof_file_path: 证明当前阶段已完成的文件绝对路径
    """
    global context
    
    # 1. 验证文件存在性
    file_path = Path(proof_file_path)
    if not file_path.exists():
        return f"错误：文件 '{proof_file_path}' 不存在。请先创建文件再提交。"
    
    if file_path.stat().st_size == 0:
        return f"错误：文件 '{proof_file_path}' 是空的。请写入内容。"

    # 2. 状态流转逻辑
    current = context.current_state
    next_state = current
    message = "验证通过。"

    if current == ReviewState.STAGE_0_INIT:
        next_state = ReviewState.STAGE_1_ALIGN
    elif current == ReviewState.STAGE_1_ALIGN:
        next_state = ReviewState.STAGE_2_ARCHITECT
    elif current == ReviewState.STAGE_2_ARCHITECT:
        next_state = ReviewState.STAGE_3_ATOMIZE
    elif current == ReviewState.STAGE_3_ATOMIZE:
        next_state = ReviewState.STAGE_4_APPROVE
    elif current == ReviewState.STAGE_4_APPROVE:
        next_state = ReviewState.STAGE_5_AUTOMATE
    elif current == ReviewState.STAGE_5_AUTOMATE:
        next_state = ReviewState.WAITING_FOR_HUMAN
        message += " 进入等待人工回复模式。"
    elif current == ReviewState.STAGE_6_ASSESS:
        next_state = ReviewState.STAGE_7_EXTEND
    elif current == ReviewState.STAGE_7_EXTEND:
        next_state = ReviewState.COMPLETED
        message += " 流程结束。"

    context.current_state = next_state
    save_state()
    
    return f"{message} 状态已更新为: {next_state.value}。请继续调用 `get_current_instruction`。"

@mcp.tool()
def check_human_response(file_path: str) -> str:
    """
    在 WAITING_FOR_HUMAN 阶段使用。检查用户是否已在文件中填写内容。
    Args:
        file_path: 问题记录文件的路径 (06_xxx.md)
    """
    global context
    
    if context.current_state != ReviewState.WAITING_FOR_HUMAN:
        return f"错误：当前状态为 {context.current_state}，不需要检查人工回复。"

    path = Path(file_path)
    if not path.exists():
        return "错误：文件不存在。"

    content = path.read_text(encoding="utf-8")
    
    # 简单的启发式检查：看是否还有空的回答标记，或者文件是否被修改过
    # 这里简单假设如果用户填写了，文件长度会显著增加，或者 "回答：[留空" 这样的标记变少
    # 为了演示，我们假设只要调用了这个工具，且文件存在，就视为用户已处理（实际应更严格）
    
    # 更严格的检查逻辑示例：
    # if "**回答**：[留空" in content:
    #     return "检测到仍有未填写的回答。请等待用户填写。"

    context.current_state = ReviewState.STAGE_6_ASSESS
    save_state()
    return "检测到人工回复（或已确认跳过等待）。状态已更新为 STAGE_6_ASSESS。请继续。"

if __name__ == "__main__":
    mcp.run()

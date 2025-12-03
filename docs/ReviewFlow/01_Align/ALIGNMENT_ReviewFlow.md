# ALIGNMENT_ReviewFlow: 需求对齐与核心机制澄清

## 1. 原始需求回顾
用户希望构建一个 MCP Server (`ReviewFlow`)，用于控制大模型按照 `6a.md` 定义的工作流执行“方案评审”任务。
核心痛点：如何确保大模型严格遵守流程节点，而不是跳过步骤或自由发挥。

## 2. 核心疑问澄清 (Q&A)

### Q: 现在的方案就能可靠控制大模型吗？
**A: 是的，但机制不同于传统编程。**
传统编程中，函数 `add(a,b)` 直接计算结果。
在 MCP + LLM 架构中，我们采用 **"导航员-执行者-检查员" (Navigator-Executor-Inspector)** 模式：
1.  **MCP (Navigator)**: 维护当前状态（如 `STAGE_1_ALIGN`）。
2.  **LLM (Executor)**: 询问 "我现在该做什么？" (`get_current_instruction`)。
3.  **MCP**: 返回具体的 **Prompt**（如 "请读取 docs/xx，分析业务，写入 docs/yy"）。
4.  **LLM**: **利用自身的智力** 执行这个 Prompt，进行分析、写作，并调用文件操作工具（`write_file`）生成结果。
5.  **LLM**: 汇报 "我做完了" (`submit_work`)。
6.  **MCP (Inspector)**: 检查结果文件是否存在/合规。如果合规 -> 切换状态；如果不合规 -> 驳回并返回错误信息。

### Q: Tool 本身怎么去完成任务？
**A: Tool 不直接完成"智力"任务，Tool 负责"定义"和"验收"任务。**
- **Tool `get_instruction()`**: 返回任务说明书。它不写代码，但它告诉 LLM "去写代码"。
- **Tool `submit_work()`**: 它是验收员。它不写代码，但它检查 "代码写了吗"。
- **LLM**: 它是唯一的劳动力。它接收 Tool 的指令，执行智力劳动，然后向 Tool 提交成果。

**总结**:
我们不是把 "写用例" 这个动作写成 Python 代码（那是做不到的），而是把 "检查用例是否写好" 和 "提供写用例的指导模版" 写成 Python 代码。

## 3. 技术实现边界
- **状态机**: `src/review_flow.py` 内部维护一个 `ReviewState` 枚举。
- **持久化**: 状态需要保存（简单起见可保存在内存或本地 JSON），防止对话中断丢失进度。
- **人机交互**: 专门的状态 `WAITING_FOR_HUMAN`，此状态下 Tool 只返回 "等待用户编辑 docs/06_xxx.md"，直到检测到用户填写内容。

## 4. 达成共识
- 确认采用 **状态机驱动 (State Machine Driven)** 架构。
- 确认 Tool 的职责是 **流程控制 (Process Control)** 而非 **业务执行 (Business Execution)**。
- 确认 LLM 依然是业务逻辑的执行主体，但被 MCP 严格约束在当前步骤中。

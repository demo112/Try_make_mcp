from mcp.server.fastmcp import FastMCP
from src.common import get_app_logger, load_config
import logging
from src.apps.six_a_test_workflow.core.workflow import WorkflowManager
from src.apps.six_a_test_workflow.core.document import DocumentHandler
from src.apps.six_a_test_workflow.core.test_case import TestCaseManager

# 1. 加载配置
default_config = {
    "log_level": "INFO"
}
config = load_config(default_config)

# 2. 初始化日志
logger = get_app_logger("six_a_test_workflow")
log_level = getattr(logging, config.get("log_level", "INFO").upper(), logging.INFO)
logger.setLevel(log_level)

logger.info(f"App started with config: {config}")

# 3. 初始化 Managers
workflow_mgr = WorkflowManager()
doc_handler = DocumentHandler()
test_case_mgr = TestCaseManager()

# 4. 初始化 MCP Server
mcp = FastMCP("six_a_test_workflow")

@mcp.tool()
def init_feature_workflow(feature_name: str) -> str:
    """
    初始化指定特性的测试工作流目录结构。
    Initialize the test workflow directory structure for a specific feature.
    
    Args:
        feature_name: The name of the feature (e.g., "UserLogin").
    """
    try:
        return workflow_mgr.init_workflow(feature_name)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def get_workflow_status(feature_name: str) -> str:
    """
    获取指定特性工作流的执行状态（各阶段文档是否存在）。
    Get the execution status of the workflow for a specific feature.
    
    Args:
        feature_name: The name of the feature.
    """
    try:
        status = workflow_mgr.get_status(feature_name)
        # Format status as readable string
        lines = [f"Status for {feature_name}:"]
        for stage, state in status.items():
            lines.append(f"- {stage}: {state}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def save_stage_doc(feature_name: str, stage: str, doc_type: str, content: str) -> str:
    """
    保存指定阶段的标准文档。
    Save a standard document for a specific stage.
    
    Args:
        feature_name: The name of the feature.
        stage: The stage directory name (e.g., "01_Align" or just "Align").
        doc_type: The document type prefix (e.g., "ALIGNMENT", "DESIGN").
        content: The markdown content of the document.
    """
    try:
        return doc_handler.save_doc(feature_name, stage, doc_type, content)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def read_stage_doc(feature_name: str, stage: str, doc_type: str) -> str:
    """
    读取指定阶段的文档。
    Read a document from a specific stage.
    
    Args:
        feature_name: The name of the feature.
        stage: The stage directory name.
        doc_type: The document type prefix.
    """
    try:
        return doc_handler.read_doc(feature_name, stage, doc_type)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def append_test_case(feature_name: str, 
                     module: str, 
                     sub_module: str, 
                     test_type: str, 
                     title: str, 
                     precondition: str, 
                     steps: str, 
                     expected_result: str, 
                     priority: str) -> str:
    """
    向用例表格追加一条测试用例。
    Append a test case to the test case table.
    
    Args:
        feature_name: The name of the feature.
        module: 一级模块 (Level 1 Module)
        sub_module: 二级模块 (Level 2 Module)
        test_type: 测试类型 (Test Type)
        title: 测试点标题 (Test Point Title)
        precondition: 前置条件 (Precondition)
        steps: 操作步骤 (Steps)
        expected_result: 预期结果 (Expected Result)
        priority: 重要性 (Priority)
    """
    case_data = {
        "module": module,
        "sub_module": sub_module,
        "test_type": test_type,
        "title": title,
        "precondition": precondition,
        "steps": steps,
        "expected_result": expected_result,
        "priority": priority
    }
    try:
        return test_case_mgr.append_case(feature_name, case_data)
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    mcp.run()

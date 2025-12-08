import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class TestCaseManager:
    def __init__(self):
        self.root_dir = Path(os.getcwd())
        self.docs_dir = self.root_dir / "docs"

    def _get_workflow_dir(self, feature_name: str) -> Path:
        safe_name = feature_name.replace("/", "_").replace("\\", "_")
        return self.docs_dir / f"{safe_name}用例编写工作流"

    def append_case(self, feature_name: str, case_data: dict) -> str:
        workflow_dir = self._get_workflow_dir(feature_name)
        if not workflow_dir.exists():
             raise FileNotFoundError(f"Workflow directory not found for {feature_name}")
             
        file_path = workflow_dir / "用例表格.md"
        
        # Define headers
        headers = ["一级模块", "二级模块", "测试类型", "测试点标题", "前置条件", "操作步骤", "预期结果", "重要性"]
        keys = ["module", "sub_module", "test_type", "title", "precondition", "steps", "expected_result", "priority"]
        
        # Prepare content to write
        lines_to_write = []
        
        # If file doesn't exist, add header
        if not file_path.exists():
            header_row = "| " + " | ".join(headers) + " |"
            separator_row = "| " + " | ".join(["---"] * len(headers)) + " |"
            lines_to_write.append(header_row)
            lines_to_write.append(separator_row)
            
        # Format data row
        # Handle newlines in content by replacing with <br> to keep table format valid
        row_values = []
        for k in keys:
            val = str(case_data.get(k, ""))
            val = val.replace("\n", "<br>")
            row_values.append(val)
            
        row_str = "| " + " | ".join(row_values) + " |"
        lines_to_write.append(row_str)
        
        try:
            with open(file_path, "a", encoding="utf-8") as f:
                for line in lines_to_write:
                    f.write(line + "\n")
            return "Successfully appended test case."
        except Exception as e:
            logger.error(f"Failed to append test case: {e}")
            raise e

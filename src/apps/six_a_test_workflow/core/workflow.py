import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class WorkflowManager:
    def __init__(self):
        # Assuming we are running from root or src/apps/...
        # But best to anchor to CWD if running as module
        self.root_dir = Path(os.getcwd())
        self.docs_dir = self.root_dir / "docs"

    def _get_workflow_dir(self, feature_name: str) -> Path:
        # Sanitizing feature name to some extent
        safe_name = feature_name.replace("/", "_").replace("\\", "_")
        return self.docs_dir / f"{safe_name}用例编写工作流"

    def init_workflow(self, feature_name: str) -> str:
        """Initialize the 6A workflow directories for a feature."""
        target_dir = self._get_workflow_dir(feature_name)
        
        subdirs = [
            "01_Align",
            "02_Architect",
            "03_Atomize",
            "04_Approve",
            "05_Automate",
            "06_Assess"
        ]
        
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
            for subdir in subdirs:
                (target_dir / subdir).mkdir(exist_ok=True)
            
            logger.info(f"Initialized workflow for {feature_name} at {target_dir}")
            return f"Successfully initialized workflow at: {target_dir}"
        except Exception as e:
            logger.error(f"Failed to init workflow: {e}")
            raise e

    def get_status(self, feature_name: str) -> dict:
        """Check which stages have files."""
        target_dir = self._get_workflow_dir(feature_name)
        status = {}
        
        subdirs = {
            "01_Align": ["ALIGNMENT", "CONSENSUS"],
            "02_Architect": ["DESIGN"],
            "03_Atomize": ["TASK"],
            "04_Approve": ["CHECKLIST"],
            "05_Automate": ["ACCEPTANCE"],
            "06_Assess": ["FINAL", "TODO"]
        }
        
        if not target_dir.exists():
            return {"status": "Not initialized"}
            
        for subdir, expected_prefixes in subdirs.items():
            stage_dir = target_dir / subdir
            if not stage_dir.exists():
                status[subdir] = "Missing Directory"
                continue
                
            files = list(stage_dir.glob("*.md"))
            found_files = [f.name for f in files]
            
            # Check if expected docs exist
            stage_status = []
            for prefix in expected_prefixes:
                # Check if any file starts with prefix
                found = any(f.startswith(prefix) for f in found_files)
                if found:
                    stage_status.append(f"{prefix}: OK")
                else:
                    stage_status.append(f"{prefix}: Missing")
            
            status[subdir] = ", ".join(stage_status)
            
        return status

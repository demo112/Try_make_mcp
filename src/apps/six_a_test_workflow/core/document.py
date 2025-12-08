import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class DocumentHandler:
    def __init__(self):
        self.root_dir = Path(os.getcwd())
        self.docs_dir = self.root_dir / "docs"

    def _get_workflow_dir(self, feature_name: str) -> Path:
        safe_name = feature_name.replace("/", "_").replace("\\", "_")
        return self.docs_dir / f"{safe_name}用例编写工作流"

    def _resolve_stage_dir(self, workflow_dir: Path, stage: str) -> Path:
        # Try to match partial stage name
        # e.g. "Align" matches "01_Align"
        if (workflow_dir / stage).exists():
            return workflow_dir / stage
        
        for subdir in workflow_dir.iterdir():
            if subdir.is_dir() and stage.lower() in subdir.name.lower():
                return subdir
        
        # Default fallback if explicit name provided but not found (will create or fail later)
        return workflow_dir / stage

    def save_doc(self, feature_name: str, stage: str, doc_type: str, content: str) -> str:
        workflow_dir = self._get_workflow_dir(feature_name)
        if not workflow_dir.exists():
            raise FileNotFoundError(f"Workflow directory not found for {feature_name}. Please init first.")
            
        stage_dir = self._resolve_stage_dir(workflow_dir, stage)
        stage_dir.mkdir(exist_ok=True)
        
        # Filename: DOC_TYPE_feature_name.md
        filename = f"{doc_type}_{feature_name}.md"
        file_path = stage_dir / filename
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"Saved doc {filename} to {stage_dir}")
            return f"Successfully saved {filename}"
        except Exception as e:
            logger.error(f"Failed to save doc: {e}")
            raise e

    def read_doc(self, feature_name: str, stage: str, doc_type: str) -> str:
        workflow_dir = self._get_workflow_dir(feature_name)
        stage_dir = self._resolve_stage_dir(workflow_dir, stage)
        filename = f"{doc_type}_{feature_name}.md"
        file_path = stage_dir / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"Document {filename} not found in {stage_dir}")
            
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

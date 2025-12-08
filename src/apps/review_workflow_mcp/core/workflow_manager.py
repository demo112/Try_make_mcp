import os
import json
from pathlib import Path
from typing import Optional, List
from .models import WorkflowState, StageEnum

STAGE_ORDER = [
    StageEnum.INIT,
    StageEnum.ALIGN,
    StageEnum.ARCHITECT,
    StageEnum.ATOMIZE,
    StageEnum.APPROVE,
    StageEnum.AUTOMATE,
    StageEnum.ASSESS,
    StageEnum.EXTEND,
    StageEnum.DONE
]

class WorkflowManager:
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.docs_root = self.root_path / "docs"
        
    def _get_project_dir(self, project_name: str) -> Path:
        return self.docs_root / project_name

    def _get_state_file(self, project_name: str) -> Path:
        return self._get_project_dir(project_name) / "workflow_state.json"

    def init_project(self, project_name: str) -> str:
        project_dir = self._get_project_dir(project_name)
        if project_dir.exists():
            # If exists, check if it's a valid project (has state file)
            state_file = self._get_state_file(project_name)
            if state_file.exists():
                return f"Project '{project_name}' already exists."
        
        # Create directories
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for stages
        subdirs = [
            "01_Align", "02_Architect", "03_Atomize", 
            "04_Approve", "05_Automate", "06_Assess"
        ]
        for subdir in subdirs:
            (project_dir / subdir).mkdir(exist_ok=True)
            
        # Create Readme
        (project_dir / "Readme.md").write_text(f"# {project_name} 评审工作流\n", encoding="utf-8")
        
        # Init state
        state = WorkflowState(project_name=project_name, current_stage=StageEnum.ALIGN)
        self._save_state(state)
        
        return f"Project '{project_name}' initialized successfully. Current stage: {state.current_stage}"

    def get_state(self, project_name: str) -> WorkflowState:
        state_file = self._get_state_file(project_name)
        if not state_file.exists():
            raise FileNotFoundError(f"Project '{project_name}' not found or not initialized.")
            
        with open(state_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return WorkflowState(**data)

    def _save_state(self, state: WorkflowState):
        state.update_timestamp()
        state_file = self._get_state_file(state.project_name)
        with open(state_file, "w", encoding="utf-8") as f:
            f.write(state.model_dump_json(indent=2))

    def advance_stage(self, project_name: str) -> str:
        state = self.get_state(project_name)
        current_idx = STAGE_ORDER.index(state.current_stage)
        
        if current_idx >= len(STAGE_ORDER) - 1:
            return "Already at the final stage."
            
        next_stage = STAGE_ORDER[current_idx + 1]
        
        # TODO: Add quality gate checks here based on existing files
        # For now, we allow manual transition
        
        state.current_stage = next_stage
        self._save_state(state)
        return f"Advanced to stage: {next_stage}"

    def save_document(self, project_name: str, filename: str, content: str) -> str:
        state = self.get_state(project_name)
        project_dir = self._get_project_dir(project_name)
        
        # Security check: prevent path traversal
        file_path = (project_dir / filename).resolve()
        if not str(file_path).startswith(str(project_dir)):
            raise ValueError("Invalid file path: must be within project directory.")
            
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        # Update state documents list
        stage_key = state.current_stage.value
        if stage_key not in state.documents:
            state.documents[stage_key] = []
        
        rel_path = str(file_path.relative_to(project_dir)).replace("\\", "/")
        if rel_path not in state.documents[stage_key]:
            state.documents[stage_key].append(rel_path)
            self._save_state(state)
            
        return f"Document saved: {rel_path}"

    def list_files(self, project_name: str) -> List[str]:
        project_dir = self._get_project_dir(project_name)
        if not project_dir.exists():
            return []
        
        files = []
        for path in project_dir.rglob("*"):
            if path.is_file():
                files.append(str(path.relative_to(project_dir)).replace("\\", "/"))
        return files

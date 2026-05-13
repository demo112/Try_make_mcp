import pytest
import os
import shutil
from pathlib import Path
from src.factory.init_app import create_app

@pytest.fixture
def temp_workspace(tmp_path):
    """
    Mock the workspace by changing cwd to tmp_path
    and creating src/apps and docs structure.
    """
    # Setup
    original_cwd = Path.cwd()
    
    # Create structure in tmp_path
    apps_dir = tmp_path / "src" / "apps"
    docs_dir = tmp_path / "docs"
    apps_dir.mkdir(parents=True)
    docs_dir.mkdir(parents=True)
    
    # Change CWD
    os.chdir(tmp_path)
    
    yield tmp_path
    
    # Teardown
    os.chdir(original_cwd)

def test_create_app_structure(temp_workspace):
    app_name = "test_app"
    display_name = "测试应用"
    
    create_app(app_name, display_name)
    
    # Verify App
    app_dir = temp_workspace / "src" / "apps" / app_name
    assert app_dir.exists()
    assert (app_dir / "server.py").exists()
    assert (app_dir / "config.json").exists()
    assert (app_dir / "tests").exists()
    assert (app_dir / "tests" / "test_server.py").exists()
    assert (app_dir / "tests" / "conftest.py").exists()
    
    # Verify Docs
    doc_dir = temp_workspace / "docs" / display_name
    assert doc_dir.exists()
    assert (doc_dir / "01_Align").exists()
    assert (doc_dir / "UserManual.md").exists()
    
    # Verify Test Content
    test_content = (app_dir / "tests" / "test_server.py").read_text(encoding="utf-8")
    assert "class McpTestClient" in test_content or "from src.testing.client import McpTestClient" in test_content
    assert display_name in test_content

def test_create_app_existing_conflict(temp_workspace, capsys):
    app_name = "conflict_app"
    display_name = "冲突应用"
    
    # First creation
    create_app(app_name, display_name)
    
    # Second creation
    create_app(app_name, display_name)
    
    captured = capsys.readouterr()
    assert "错误: 应用目录已存在" in captured.out

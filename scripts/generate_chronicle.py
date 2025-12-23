import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Set, Tuple
import git

def generate_chronicle():
    root_dir = Path(os.getcwd())
    repo = git.Repo(root_dir)
    
    # Configuration
    output_file = root_dir / "docs" / "PROJECT_CHRONICLE.md"
    
    # Data structure: category -> date -> list of messages
    chronicle_data: Dict[str, Dict[str, List[str]]] = {}
    
    # 1. Analyze Commits
    print("🔍 Analyzing git history...")
    for commit in repo.iter_commits(reverse=True): # Process from oldest to newest
        date_str = datetime.fromtimestamp(commit.committed_date).strftime('%Y-%m-%d')
        message = commit.message.split('\n')[0].strip()
        
        # Determine categories affected by this commit
        categories = set()
        try:
            # Note: commit.stats.files is expensive for large repos, but fine for this scale
            for file_path in commit.stats.files.keys():
                path = Path(file_path)
                parts = path.parts
                
                if "src" in parts and "apps" in parts:
                    # It's an app
                    try:
                        app_idx = parts.index("apps") + 1
                        if app_idx < len(parts):
                            app_name = parts[app_idx]
                            categories.add(f"App: {app_name}")
                    except ValueError:
                        pass
                elif "src" in parts and "factory" in parts:
                    categories.add("MCP Factory")
                elif "docs" in parts:
                    # Try to see if it's app specific docs
                    if len(parts) > 1:
                         # e.g. docs/todo_list/...
                         potential_app = parts[1]
                         # Check if this corresponds to a known app (heuristic)
                         # For now, just categorize as Docs or specific app if matched later
                         pass
                    categories.add("Documentation")
                else:
                    categories.add("General")
        except Exception as e:
            # Sometimes stats fails on merge commits or others
            continue
            
        # Clean up categories
        if not categories:
            categories.add("General")
            
        # Add to data
        for category in categories:
            if category not in chronicle_data:
                chronicle_data[category] = {}
            if date_str not in chronicle_data[category]:
                chronicle_data[category][date_str] = []
            
            # Avoid duplicate messages for the same day/category
            if message not in chronicle_data[category][date_str]:
                chronicle_data[category][date_str].append(message)

    # 2. Generate Markdown Content
    print("📝 Generating chronicle document...")
    
    content = ["# 项目编年史 (Project Chronicle)", ""]
    content.append("> 本文档由脚本自动生成，展示了 MCP 工厂及各应用的演化历程。")
    content.append("")
    
    # 2.1 Mermaid Gantt Chart
    content.append("## 演化时间轴 (Evolution Timeline)")
    content.append("")
    content.append("```mermaid")
    content.append("gantt")
    content.append('    title 项目演化历程')
    content.append('    dateFormat YYYY-MM-DD')
    content.append('    axisFormat %m-%d')
    content.append('')
    
    # Sort categories to keep Factory at top, then Apps
    sorted_categories = sorted(chronicle_data.keys())
    # Custom sort: Factory first, then Apps, then General
    def category_rank(cat):
        if "Factory" in cat: return 0
        if "App:" in cat: return 1
        return 2
    sorted_categories.sort(key=category_rank)

    for category in sorted_categories:
        content.append(f"    section {category}")
        dates = sorted(chronicle_data[category].keys())
        
        for date_str in dates:
            msgs = chronicle_data[category][date_str]
            # Combine messages or pick representative
            # For Gantt, we need concise labels.
            # Strategy: "Update (3 commits)" or the single message
            if len(msgs) == 1:
                label = msgs[0].replace(':', ' ').replace('"', "'").replace('#', '')
            else:
                label = f"{msgs[0].replace(':', ' ')} (+{len(msgs)-1})"
            
            # Truncate label
            if len(label) > 30:
                label = label[:27] + "..."
                
            content.append(f"    {label} : {date_str}, 1d")
        
        content.append("")
        
    content.append("```")
    content.append("")
    
    # 2.2 Detailed Log
    content.append("## 详细变更记录 (Detailed Changelog)")
    
    for category in sorted_categories:
        content.append(f"### {category}")
        dates = sorted(chronicle_data[category].keys(), reverse=True)
        for date_str in dates:
            content.append(f"- **{date_str}**")
            for msg in chronicle_data[category][date_str]:
                content.append(f"  - {msg}")
        content.append("")

    # 3. Write to file
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(content))
        
    print(f"✅ Chronicle generated at: {output_file}")

if __name__ == "__main__":
    generate_chronicle()

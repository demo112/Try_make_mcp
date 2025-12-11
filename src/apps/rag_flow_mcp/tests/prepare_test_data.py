import os
import re
import random

from pathlib import Path

# Configuration
# target_file_path = r"c:\Users\Administrator\Documents\trae_projects\use_rag_mcp\docs\AI智能服务评审工作流\06_方案业务评审问题_AI智能服务.md"
# Use a relative path or environment variable if possible, but keeping hardcoded for now if external.
target_file_path = r"c:\Users\Administrator\Documents\trae_projects\use_rag_mcp\docs\AI智能服务评审工作流\06_方案业务评审问题_AI智能服务.md"

# Output to a directory relative to this script
current_dir = Path(__file__).parent
output_dir = current_dir / "materials"

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

def restore_target_file(file_path):
    print(f"Restoring {file_path}...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Regex to remove **AI 参考建议** blocks
        # Pattern: looks for **AI 参考建议** ... up to the line before **回答**
        # We assume **回答** starts a new line.
        pattern = re.compile(r'\n\*\*AI 参考建议\*\*：.*?(?=\n\*\*回答\*\*|\Z)', re.DOTALL)
        
        new_content = pattern.sub('', content)
        
        # Clean up any potential double newlines left behind if needed, 
        # but usually simply removing the block is enough.
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Successfully restored target file.")
        
    except Exception as e:
        print(f"Error restoring file: {e}")

def generate_test_materials(output_dir, count=10):
    print(f"Generating {count} test materials in {output_dir}...")
    
    questions = [
        {
            "id": 1,
            "title": "订阅过期数据保留策略",
            "options": ["A: 立即删除", "B: 保留数据 30 天", "C: 永久保留数据"],
            "context_variations": [
                "考虑到用户体验，我们不能立即删除。",
                "由于存储成本高昂，我们需要尽快清理。",
                "法律法规要求我们保留数据一段时间。",
                "竞品通常保留3个月，我们应该跟进。"
            ]
        },
        {
            "id": 2,
            "title": "退订生效时间",
            "options": ["A: 立即终止权益", "B: 权益持续有效，直到当前周期结束"],
            "context_variations": [
                "为了减少纠纷，建议权益保留到期末。",
                "立即终止可以防止用户薅羊毛。",
                "参考Netflix的做法，通常是到期结束。",
                "财务结算比较麻烦，建议立即终止并退款。"
            ]
        },
        {
            "id": 3,
            "title": "人脸库容量上限",
            "type": "number",
            "values": [10, 20, 50, 100],
            "context_variations": [
                "设备内存有限，不能太多。",
                "家庭场景一般不超过10人。",
                "小微企业场景可能需要50人。",
                "算法性能测试表明100人是上限。"
            ]
        },
        {
            "id": 4,
            "title": "夜视模式识别策略",
            "options": ["A: 允许识别", "B: 强制关闭人脸识别"],
            "context_variations": [
                "红外模式下特征丢失严重，建议关闭。",
                "虽然不准，但用户有需求，可以允许但给提示。",
                "为了安全起见，夜视模式不应该进行识别。",
                "算法团队优化了夜视模型，可以尝试开启。"
            ]
        },
        {
            "id": 5,
            "title": "包裹报警频控",
            "options": ["A: 仅在状态变化时推送一次", "B: 状态变化时推送，后续每隔 X 小时重复提醒"],
            "context_variations": [
                "避免打扰用户，一次就够了。",
                "包裹很重要，怕用户没看见，需要重复提醒。",
                "可以设置一个勿扰模式，默认重复提醒。",
                "状态变化最重要，后续提醒意义不大。"
            ]
        },
        {
            "id": 6,
            "title": "宠物误报处理UI",
            "options": ["A: 不做特殊处理", "B: 在划区界面提示"],
            "context_variations": [
                "UI太复杂了，不需要提示。",
                "用户经常投诉这个问题，必须提示。",
                "可以在帮助中心说明，不用在主界面提示。",
                "划区时提示效果最好。"
            ]
        },
        {
            "id": 7,
            "title": "人脸照片质量门控",
            "options": ["A: 不校验", "B: 强制校验"],
            "context_variations": [
                "校验会降低录入成功率，影响体验。",
                "烂数据进去也是白搭，必须校验。",
                "可以先提示但不强制。",
                "为了保证识别率，只能牺牲一点录入体验。"
            ]
        }
    ]

    for i in range(1, count + 1):
        filename = f"Answer_Source_{i:02d}.md"
        filepath = os.path.join(output_dir, filename)
        
        content = f"# AI智能服务业务规则决策参考 v{i}\n\n"
        content += f"本文档包含针对AI智能服务评审问题的决策依据。版本: {i}\n\n"
        
        for q in questions:
            content += f"## {q['id']}. {q['title']}\n\n"
            
            # Decide answer
            if q.get("type") == "number":
                ans = random.choice(q["values"])
                ans_str = f"{ans}"
            else:
                ans = random.choice(q["options"])
                ans_str = ans
            
            ctx = random.choice(q["context_variations"])
            
            content += f"**决策结论**: {ans_str}\n\n"
            content += f"**决策依据**: {ctx}\n\n"
            content += f"**相关背景**: 在版本v{i}的讨论中，我们认为应该优先考虑{random.choice(['用户体验', '系统性能', '成本控制', '开发进度'])}。\n\n"
            content += "---\n\n"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Generated {filename}")

if __name__ == "__main__":
    restore_target_file(target_file_path)
    generate_test_materials(output_dir)

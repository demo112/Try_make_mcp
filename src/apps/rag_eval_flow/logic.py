import os
import csv
import pandas as pd
import pathlib
import json
import logging
from typing import List, Dict, Optional
from litellm import completion

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Default Model Configuration
# Users should set GEMINI_API_KEY in .env
MODEL_NAME = "gemini/gemini-2.0-flash-exp"

class LogicError(Exception):
    pass

def _call_llm(prompt: str, model: str = MODEL_NAME) -> str:
    """Helper to call LLM via litellm"""
    try:
        response = completion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"LLM Call failed: {e}")
        raise LogicError(f"LLM Call failed: {str(e)}")

def generate_qa_pairs(source_path: str, output_path: str, num_pairs: int = 20) -> str:
    """
    Generate QA pairs from a knowledge base file.
    """
    source_file = pathlib.Path(source_path)
    if not source_file.exists():
        raise FileNotFoundError(f"Source file not found: {source_path}")
    
    # Read content
    try:
        content = source_file.read_text(encoding='utf-8')
    except Exception as e:
        raise LogicError(f"Failed to read source file: {e}")
        
    # Truncate if too long (simple handling for now)
    # Gemini 2.0 has large context, but let's be safe.
    if len(content) > 100000:
        logger.warning("Content too long, truncating to first 100k chars.")
        content = content[:100000]

    prompt = f"""
    你是一个专业的测试工程师。请阅读以下文档内容，生成 {num_pairs} 个高质量的问答对。
    问题应覆盖文档的关键信息，答案应准确且简洁。
    
    请严格返回 JSON 格式列表，格式如下：
    [
        {{"question": "问题1", "answer": "答案1"}},
        {{"question": "问题2", "answer": "答案2"}}
    ]
    
    文档内容:
    {content}
    """
    
    response_text = _call_llm(prompt)
    
    # Extract JSON
    try:
        # Simple cleanup for markdown code blocks
        clean_text = response_text.replace("```json", "").replace("```", "").strip()
        qa_list = json.loads(clean_text)
    except json.JSONDecodeError:
        logger.error(f"Failed to parse LLM response as JSON: {response_text}")
        raise LogicError("Failed to parse LLM response as JSON")
        
    if not isinstance(qa_list, list):
        raise LogicError("LLM response is not a list")
        
    # Save to CSV
    output_file = pathlib.Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    df = pd.DataFrame(qa_list)
    if 'question' not in df.columns or 'answer' not in df.columns:
         raise LogicError("Generated JSON missing 'question' or 'answer' keys")
         
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    return f"Successfully generated {len(df)} QA pairs to {output_path}"

def run_rag_simulation(dataset_path: str, knowledge_base_path: str, output_path: str) -> str:
    """
    Run RAG simulation: Read questions, retrieve context (full doc), generate answers.
    """
    dataset_file = pathlib.Path(dataset_path)
    kb_file = pathlib.Path(knowledge_base_path)
    
    if not dataset_file.exists():
        raise FileNotFoundError(f"Dataset file not found: {dataset_path}")
    if not kb_file.exists():
        raise FileNotFoundError(f"Knowledge base file not found: {knowledge_base_path}")
        
    # Read Questions
    try:
        df = pd.read_csv(dataset_file)
    except Exception as e:
        raise LogicError(f"Failed to read CSV: {e}")
        
    if 'question' not in df.columns:
        raise LogicError("CSV must contain 'question' column")
        
    # Read KB Context
    context = kb_file.read_text(encoding='utf-8')
    if len(context) > 100000:
        context = context[:100000] # Simple truncation
        
    results = []
    
    for idx, row in df.iterrows():
        question = row['question']
        logger.info(f"Processing Q{idx+1}: {question}")
        
        prompt = f"""
        基于以下参考资料回答问题。如果资料中没有答案，请说不知道。
        
        参考资料:
        {context}
        
        问题: {question}
        """
        
        answer = _call_llm(prompt)
        results.append({
            "question": question,
            "generated_answer": answer
        })
        
    # Save Results
    output_file = pathlib.Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    result_df = pd.DataFrame(results)
    result_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    return f"Successfully processed {len(results)} questions. Saved to {output_path}"

def evaluate_results(qa_result_path: str, standard_dataset_path: str, output_path: str) -> str:
    """
    Evaluate generated answers against standard answers.
    """
    qa_file = pathlib.Path(qa_result_path)
    std_file = pathlib.Path(standard_dataset_path)
    
    if not qa_file.exists() or not std_file.exists():
        raise FileNotFoundError("Input files not found")
        
    df_qa = pd.read_csv(qa_file)
    df_std = pd.read_csv(std_file)
    
    # Merge on question. Assuming questions are identical strings.
    # In practice, fuzzy matching might be needed if questions were modified, 
    # but here we assume strict pipeline flow.
    merged = pd.merge(df_qa, df_std, on='question', how='inner', suffixes=('_gen', '_std'))
    
    if merged.empty:
        raise LogicError("No matching questions found between result and standard dataset")
    
    eval_results = []
    
    for idx, row in merged.iterrows():
        q = row['question']
        gen_ans = row.get('generated_answer', row.get('answer_gen', '')) # Handle column naming
        std_ans = row.get('answer', row.get('answer_std', ''))
        
        prompt = f"""
        请作为公正的判卷人，评估【考生回答】相对于【标准答案】的准确性。
        
        问题: {q}
        标准答案: {std_ans}
        考生回答: {gen_ans}
        
        请严格返回 JSON 格式，包含:
        - score: 0-10 (整数)
        - reason: 简短评价理由
        
        示例: {{"score": 9, "reason": "意思完全一致，只是措辞略有不同"}}
        """
        
        resp = _call_llm(prompt)
        
        try:
            clean_resp = resp.replace("```json", "").replace("```", "").strip()
            eval_data = json.loads(clean_resp)
            score = eval_data.get('score', 0)
            reason = eval_data.get('reason', 'Parse Error')
        except:
            score = 0
            reason = "Failed to parse evaluation"
            
        eval_results.append({
            "question": q,
            "standard_answer": std_ans,
            "generated_answer": gen_ans,
            "score": score,
            "reason": reason
        })
        
    output_file = pathlib.Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    out_df = pd.DataFrame(eval_results)
    out_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    avg_score = out_df['score'].mean()
    return f"Evaluation complete. Average Score: {avg_score:.2f}. Saved to {output_path}"

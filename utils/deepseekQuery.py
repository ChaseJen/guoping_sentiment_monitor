
# 😊和ai问答相关的代码写这里


from flask import Flask, request, render_template, jsonify
from elasticsearch import Elasticsearch
import json
from openai import OpenAI

es = Elasticsearch("http://localhost:9200") 
client = OpenAI(
    api_key="sk-6b251c2cdf334a40b298d594d27801cf",
    base_url="https://api.deepseek.com"
)
from openai import OpenAI

# 初始化 DeepSeek 客户端
client = OpenAI(
    api_key="sk-6b251c2cdf334a40b298d594d27801cf",
    base_url="https://api.deepseek.com"
)
def call_deepseek(query, context):
    """
    给定用户query和语义检索到的上下文内容，调用DeepSeek生成答案
    """
    prompt = f"""你是一个擅长社交媒体舆情分析的AI助手。请根据以下微博内容，尽量详细且准确地回答用户问题。回答字数要多一点。
如果相关内容不足以回答，请礼貌地说明“抱歉，我无法回答该问题”。

【用户问题】
{query}

【相关微博内容】
{context}

请直接给出回答，不要重复问题或上下文。
"""

    try:
        # 调用 DeepSeek 模型生成回答
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个社交媒体舆情分析助手"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            stream=False
        )
        answer = response.choices[0].message.content.strip()
         
        if not answer:
            return "抱歉，我无法生成有效回答，请稍后再试。"
        return answer

    except Exception as e:
        print(f"调用 DeepSeek 出错：{e}")
        return "抱歉，我暂时无法生成回答，请稍后再试。"



def semantic_search(query, top_k=20):
    # 使用 ES 进行语义搜索（现阶段先使用es原生的相关度判断机制）
    res = es.search(index="guoping", query={
        "match": {
            "text": query
        }
    }, size=top_k)

    results = []
    for hit in res["hits"]["hits"]:
        source = hit["_source"]
        results.append({
            "text": source["text"],
            "score": source.get("score", "无"),
            "created_at": source.get("created_at", ""),
            "screen_name": source.get("screen_name", "未知用户"),
            "user_authentication": source.get("user_authentication", "普通用户"),
            "reposts_count": source.get("reposts_count", 0),
            "comments_count": source.get("comments_count", 0),
            "attitudes_count": source.get("attitudes_count", 0)
            
        })
    return results



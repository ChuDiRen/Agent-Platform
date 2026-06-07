"""接口文档分析服务层 — 提供给 API 端点使用"""
from app.agents.api_document.tools import analyze_api_document as _analyze


def analyze_api_document(content: str, extra_prompt: str = ""):
    """分析接口文档，返回发现的问题。"""
    result = _analyze.invoke({"content": content})
    import json
    data = json.loads(result)
    return data

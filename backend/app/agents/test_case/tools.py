"""测试用例生成工具"""
from __future__ import annotations
import json
from langchain_core.tools import tool


@tool
def generate_cases_from_doc(content: str, module_name: str = "", case_type: str = "all") -> str:
    """从需求/接口文档生成测试用例。

    Args:
        content: 文档内容（需求描述或接口定义）。
        module_name: 模块名称。
        case_type: 用例类型 — all(全部)/positive(正向)/negative(反向)/boundary(边界)。
    """
    # 提取关键信息
    lines = content.strip().split("\n")
    has_api = any(kw in content.lower() for kw in ["api", "接口", "请求", "url", "method", "get", "post", "put", "delete"])
    has_ui = any(kw in content.lower() for kw in ["页面", "按钮", "输入框", "弹窗", "点击", "界面"])

    doc_type = "api" if has_api else ("ui" if has_ui else "general")

    cases = []
    idx = 1

    # 正向用例
    if case_type in ("all", "positive"):
        cases.append({
            "id": f"TC-{idx:03d}",
            "name": f"验证{module_name or '模块'}正常功能流程",
            "priority": 1,
            "precondition": "系统正常运行，用户已登录",
            "steps": "1. 按文档描述执行正常操作流程\n2. 输入合法数据\n3. 提交请求",
            "expected": "操作成功，返回预期结果",
            "type": "positive",
        })
        idx += 1

    # 反向用例
    if case_type in ("all", "negative"):
        cases.append({
            "id": f"TC-{idx:03d}",
            "name": f"验证{module_name or '模块'}输入非法数据的错误处理",
            "priority": 1,
            "precondition": "系统正常运行",
            "steps": "1. 输入非法/空/超长数据\n2. 提交请求",
            "expected": "返回明确的错误提示，不泄露系统内部信息",
            "type": "negative",
        })
        idx += 1

    if has_api:
        cases.extend([
            {"id": f"TC-{idx:03d}", "name": "验证接口参数缺失时的响应", "priority": 2,
             "precondition": "接口可用", "steps": "1. 不传必选参数\n2. 发送请求",
             "expected": "返回 400 或业务错误码，提示缺少必要参数", "type": "negative"},
            {"id": f"TC-{idx+1:03d}", "name": "验证接口超时处理", "priority": 3,
             "precondition": "网络正常", "steps": "1. 模拟服务端延迟\n2. 发送请求",
             "expected": "客户端正确处理超时，不出现白屏或卡死", "type": "negative"},
        ])
        idx += 2

    if has_ui:
        cases.extend([
            {"id": f"TC-{idx:03d}", "name": "验证页面加载和初始状态", "priority": 1,
             "precondition": "用户已登录", "steps": "1. 进入页面\n2. 检查各元素是否正确显示",
             "expected": "页面加载完成，所有元素显示正确", "type": "positive"},
            {"id": f"TC-{idx+1:03d}", "name": "验证表单必填项校验", "priority": 1,
             "precondition": "在表单页面", "steps": "1. 不填写必填项\n2. 点击提交",
             "expected": "显示必填项提示，阻止提交", "type": "negative"},
        ])
        idx += 2

    return json.dumps({
        "module": module_name,
        "doc_type": doc_type,
        "total_cases": len(cases),
        "cases": cases,
    }, ensure_ascii=False, indent=2)


@tool
def analyze_boundary_values(field_name: str, field_type: str = "string", constraints: str = "") -> str:
    """分析单个字段的边界值测试数据。

    Args:
        field_name: 字段名称。
        field_type: 字段类型 — string/number/email/phone/password/date。
        constraints: 约束条件，如 "长度6-20位"。
    """
    boundaries = {
        "string": ["空字符串", "1个字符", "最大长度", "特殊字符", "中文", "emoji", "SQL注入"],
        "number": ["0", "负数", "最小值", "最大值", "小数", "非数字字符串"],
        "email": ["无@符号", "无域名", "多个@", "中文邮箱", "超长地址"],
        "phone": ["10位", "12位", "非1开头", "含字母", "空号段"],
        "password": ["纯数字", "纯字母", "含特殊字符", "最短", "最长", "含空格"],
        "date": ["昨天", "今天", "明天", "闰年2月29", "非闰年2月29", "12月31日"],
    }

    values = boundaries.get(field_type, boundaries["string"])

    return json.dumps({
        "field": field_name,
        "type": field_type,
        "constraints": constraints,
        "boundary_values": values,
        "test_count": len(values),
    }, ensure_ascii=False, indent=2)


@tool
def suggest_edge_cases(content: str, domain: str = "general") -> str:
    """根据文档内容建议容易遗漏的异常测试场景。

    Args:
        content: 需求或接口文档内容。
        domain: 业务领域 — general/ecommerce/finance/social/enterprise。
    """
    general_edges = [
        "并发操作: 同时提交多次请求",
        "网络中断: 操作过程中断网",
        "会话过期: Token 失效后操作",
        "权限变更: 操作过程中权限被收回",
        "数据被删: 操作的目标数据被他人删除",
        "超时重试: 请求超时后重复提交",
        "浏览器回退: 操作后点击浏览器返回",
        "多标签页: 同时打开多个页面操作",
    ]

    return json.dumps({
        "domain": domain,
        "edge_cases": general_edges,
        "total": len(general_edges),
    }, ensure_ascii=False, indent=2)

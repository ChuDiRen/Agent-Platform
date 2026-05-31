from app.schemas.document import RequirementFinding, RequirementReviewRequest, RequirementReviewResponse


def review_requirement(payload: RequirementReviewRequest) -> RequirementReviewResponse:
    content = payload.content
    findings = [
        RequirementFinding(
            id="post-login-routing",
            title="缺少登录成功后的跳转逻辑说明",
            description=(
                "需求中描述了登录成功后应跳转至对应权限的界面，但未明确具体跳转目标"
                "（如首页URL、默认工作台等），也未说明如何确定用户权限及对应视图，建议补充。"
            ),
            severity="high",
            category="流程完整性",
            adopted=True,
        ),
        RequirementFinding(
            id="username-format",
            title="未定义用户名输入框的具体格式要求",
            description=(
                "需求未规定用户名输入框支持的格式（如仅允许手机号、邮箱或用户名字符串），"
                "也未说明长度限制、特殊字符限制等，可能导致测试时无法确认输入合法性校验规则。"
            ),
            severity="high",
            category="输入校验",
            adopted=True,
        ),
        RequirementFinding(
            id="password-policy",
            title="密码输入框缺乏最小长度和复杂度要求",
            description=(
                "需求提到输入密码，但未说明密码是否需满足复杂度策略（如至少8位、包含数字字母等），"
                "这会影响安全测试用例的设计，建议明确密码策略。"
            ),
            severity="medium",
            category="安全规则",
            adopted=True,
        ),
        RequirementFinding(
            id="password-visibility",
            title="缺少密码可见性切换功能的交互细节",
            description="界面原型包含密码输入框，但未说明是否支持显示/隐藏密码以及切换后的安全处理。",
            severity="low",
            category="交互细节",
        ),
        RequirementFinding(
            id="login-retry-policy",
            title="未覆盖多次登录失败的处理机制",
            description="需求未说明连续登录失败后的锁定、验证码、错误提示和重试次数限制。",
            severity="medium",
            category="异常场景",
        ),
    ]

    if "登录" not in content:
        findings = [
            RequirementFinding(
                id="scope-clarity",
                title="需求范围描述不够明确",
                description="当前内容缺少清晰的功能目标、入口、输入输出和异常处理说明，建议补充完整。",
                severity="medium",
                category="范围清晰度",
                adopted=True,
            )
        ]

    if payload.extra_prompt:
        findings.append(
            RequirementFinding(
                id="extra-focus",
                title="已结合补充评审要求",
                description=f"补充要求：{payload.extra_prompt}",
                severity="low",
                category="补充要求",
            )
        )

    return RequirementReviewResponse(
        document_id=payload.document_id,
        title=payload.title,
        findings=findings,
    )

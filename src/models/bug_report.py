class BugReport:
        
    def __init__(
        self,
        title,
        description,
        error_code,
        bug_category,
        bug_domain,
        tech_stack,
        severity,
        environment,
        developer_role,
        root_cause,
        suggested_fix,
        explanation,
        created_at
    ):        
        self.title = title
        self.description = description
        self.error_code = error_code
        self.bug_category = bug_category
        self.bug_domain = bug_domain
        self.tech_stack = tech_stack
        self.severity = severity
        self.environment = environment
        self.developer_role = developer_role
        self.root_cause = root_cause
        self.suggested_fix = suggested_fix
        self.explanation = explanation
        self.created_at = created_at

from datetime import datetime


class BugReport:

    def __init__(
            self,
            title: str,
            error_code: int,
            bug_domain: str,
            tech_stack: str,
            severity: str,
            environment: str,
            developer_role: str,
            created_at: datetime
    ):
        self.title = title
        self.error_code = error_code
        self.bug_domain = bug_domain
        self.tech_stack = tech_stack
        self.severity = severity
        self.environment = environment
        self.developer_role = developer_role
        self.created_at = created_at

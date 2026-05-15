from datetime import datetime
from typing import List


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

    @staticmethod
    def parse_csv(cleaned_csv) -> List["BugReport"]:
        """
        Converte o DataFrame inteiro em lista de BugReport.

        - Cada linha vira um BugReport
        - Linhas inválidas são ignoradas
        - Se todas falharem → retorna lista vazia
        """

        reports = []

        for _, row in cleaned_csv.iterrows():
            try:
                reports.append(BugReport(**row.to_dict()))
            except (ValueError, TypeError):
                continue

        return reports
"""Falha quando uma nova consulta de modelo multiempresa omite company_id.

Consultas globais intencionais devem trazer `tenant-scope: global` na mesma
instrucao ou na linha imediatamente anterior, tornando a excecao auditavel.
"""
import ast
import unittest
from pathlib import Path


TENANT_MODELS = {
    "User", "Customer", "Product", "Category", "PromotionConfig",
    "PromotionAudit", "PointsTransaction", "WhatsAppMessage", "UserAudit",
}
SOURCE_ROOTS = (Path("app/routes"), Path("app/services"))


class TenantIsolationStaticTest(unittest.TestCase):
    def test_queries_de_modelos_multiempresa_declaram_company_id(self):
        violations = []
        for root in SOURCE_ROOTS:
            for path in root.glob("*.py"):
                source = path.read_text(encoding="utf-8-sig")
                lines = source.splitlines()
                tree = ast.parse(source, filename=str(path))
                parents = {}
                for parent in ast.walk(tree):
                    for child in ast.iter_child_nodes(parent):
                        parents[child] = parent

                for node in ast.walk(tree):
                    if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                        continue
                    if node.func.attr != "query" or not node.args:
                        continue
                    target = node.args[0]
                    model = target.id if isinstance(target, ast.Name) else None
                    if model not in TENANT_MODELS:
                        continue
                    statement = node
                    while statement in parents and not isinstance(statement, ast.stmt):
                        statement = parents[statement]
                    segment = ast.get_source_segment(source, statement) or ""
                    previous = lines[statement.lineno - 2] if statement.lineno > 1 else ""
                    if "company_id" not in segment and "tenant-scope: global" not in segment and "tenant-scope: global" not in previous:
                        violations.append(f"{path}:{statement.lineno} consulta {model} sem company_id")

        self.assertFalse(violations, "\n" + "\n".join(violations))


if __name__ == "__main__":
    unittest.main()

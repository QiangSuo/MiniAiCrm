from datetime import UTC, datetime
from typing import Any

from app.application.permission_service import PermissionGuard
from app.ports.repository import DemoRepository


class QuestionService:
    def __init__(self, repository: DemoRepository, permission_guard: PermissionGuard):
        self.repository = repository
        self.permission_guard = permission_guard

    def answer(self, customer_id: str, user_id: str, question: str) -> dict[str, Any]:
        self.permission_guard.require(customer_id, user_id)
        snapshot = self.repository.customer_snapshot(customer_id)
        facts: list[dict[str, str]] = []
        sources: list[dict[str, str]] = []

        for contact in snapshot["contacts"]:
            facts.append(
                {
                    "statement": f"已接触关键联系人{contact['name']}，具体职务仍待确认。",
                    "confidence": "confirmed",
                    "source_id": contact["source_proposal_id"],
                }
            )
            sources.append(
                {
                    "source_id": contact["source_proposal_id"],
                    "type": "confirmed_progress_proposal",
                    "label": "已确认拜访进展",
                }
            )
        for opportunity in snapshot["opportunities"]:
            if opportunity["priority_direction"] != "业务方向待确认":
                facts.append(
                    {
                        "statement": f"客户提出{opportunity['priority_direction']}。",
                        "confidence": "single_source",
                        "source_id": opportunity["source_proposal_id"],
                    }
                )
            if opportunity["amount_cny"] is not None:
                facts.append(
                    {
                        "statement": (
                            f"预算线索为约{opportunity['amount_cny'] // 10_000}万元，"
                            "尚未正式确认。"
                        ),
                        "confidence": opportunity["confidence"],
                        "source_id": opportunity["source_proposal_id"],
                    }
                )
            sources.append(
                {
                    "source_id": opportunity["source_proposal_id"],
                    "type": "confirmed_progress_proposal",
                    "label": "已确认商机线索",
                }
            )
        for action in snapshot["actions"]:
            facts.append(
                {
                    "statement": (
                        f"行动承诺：{action['description']}，"
                        f"截止 {action['due_date'] or '待确认'}。"
                    ),
                    "confidence": "confirmed",
                    "source_id": action["source_proposal_id"],
                }
            )
            sources.append(
                {
                    "source_id": action["source_proposal_id"],
                    "type": "confirmed_progress_proposal",
                    "label": "已确认行动承诺",
                }
            )

        if not facts:
            facts.append(
                {
                    "statement": "当前只有客户基础档案，尚无已确认的商务进展。",
                    "confidence": "confirmed",
                    "source_id": customer_id,
                }
            )
            sources.append(
                {"source_id": customer_id, "type": "customer", "label": "客户基础档案"}
            )

        return {
            "customer_id": customer_id,
            "question": question,
            "data_cutoff": datetime.now(UTC).isoformat(),
            "summary": "当前突破应围绕决策人、优先场景和方案承诺三条线推进。",
            "facts": facts,
            "inferences": [
                "李总可能是推进决策链的关键入口，但其正式角色尚未核实。",
                "财务与采购是最适合形成首批业务价值证明的场景。",
                "月底方案节点是推动预算与决策机制显性化的窗口。",
            ],
            "recommendations": [
                "确认李总的正式职务、决策权和可协调的关键部门。",
                "将财务与采购拆成可量化的两项优先场景并补充成功指标。",
                "在整体方案中单列预算依据、审批路径和下一次客户确认节点。",
            ],
            "sources": self._unique_sources(sources),
            "missing_information": [
                "李总正式职务与决策角色",
                "预算审批状态",
                "财务与采购场景的量化成功指标",
                "最终决策人与采购流程",
            ],
        }

    @staticmethod
    def _unique_sources(sources: list[dict[str, str]]) -> list[dict[str, str]]:
        unique: dict[tuple[str, str], dict[str, str]] = {}
        for source in sources:
            unique[(source["source_id"], source["type"])] = source
        return list(unique.values())

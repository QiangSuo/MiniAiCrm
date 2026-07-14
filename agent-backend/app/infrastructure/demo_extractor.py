from typing import Any


class DemoExtractor:
    """Deterministic extractor for the fixed, offline demonstration scenarios."""

    def extract_progress(self, text: str) -> dict[str, Any]:
        amount = None
        if "八千万" in text or "8000万" in text:
            amount = 80_000_000
        elif "一亿" in text or "1亿" in text:
            amount = 100_000_000

        contact_name = "李总" if "李总" in text else "待确认联系人"
        direction = "财务和采购优先" if "财务" in text and "采购" in text else "业务方向待确认"
        due_date = "2026-07-31" if "月底" in text else None

        changes: list[dict[str, Any]] = [
            {
                "entity_type": "contact",
                "operation": "upsert",
                "data": {
                    "contact_id": "CONTACT-DEMO-LI",
                    "name": contact_name,
                    "role": "客户关键联系人（具体职务待确认）",
                    "influence": "关键",
                },
            },
            {
                "entity_type": "opportunity",
                "operation": "upsert",
                "data": {
                    "opportunity_id": "OPP-DEMO-001",
                    "name": "集团数字化建设机会",
                    "stage": "需求澄清",
                    "amount_cny": amount,
                    "budget_note": (
                        f"预算线索约{amount // 10_000}万元，来自拜访单一来源，待客户正式确认"
                        if amount
                        else "预算待确认"
                    ),
                    "confidence": "single_source",
                    "priority_direction": direction,
                },
            },
            {
                "entity_type": "action",
                "operation": "upsert",
                "data": {
                    "action_id": "ACTION-DEMO-PROPOSAL",
                    "description": "提交集团数字化整体方案",
                    "owner_user_id": "u-demo-owner",
                    "due_date": due_date,
                    "status": "open",
                },
            },
        ]
        missing_fields = ["李总职位", "预算审批状态", "方案提交具体日期"]
        if contact_name == "待确认联系人":
            missing_fields.append("客户联系人")
        if amount is None:
            missing_fields.append("预算金额")
        return {
            "changes": changes,
            "missing_fields": missing_fields,
            "original_text": text,
        }

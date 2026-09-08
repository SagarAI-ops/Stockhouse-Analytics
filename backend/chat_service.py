from typing import List

import pandas as pd

from analytics_engine import get_anomalies, get_kpis
from llm_service import GeminiService
from models import ChatMessage
from prompts import (
    ANALYTICS_SYSTEM_PROMPT,
    DIAGNOSTIC_SYSTEM_PROMPT,
    FORECASTING_SYSTEM_PROMPT,
)


class ChatService:
    """Routes a user question to the right prompt and attaches data context."""

    def __init__(self, llm: GeminiService):
        self.llm = llm

    def handle_message(
        self,
        message: str,
        history: List[ChatMessage],
        df: pd.DataFrame,
    ) -> str:
        intent = self._classify(message)
        context = self._build_context(df, intent)
        system = {
            "forecast": FORECASTING_SYSTEM_PROMPT,
            "diagnostic": DIAGNOSTIC_SYSTEM_PROMPT,
        }.get(intent, ANALYTICS_SYSTEM_PROMPT)
        user_payload = f"{context}\n\nUser question: {message}"
        return self.llm.generate_response(user_payload, history, system_prompt=system)

    def _classify(self, message: str) -> str:
        text = message.lower()
        if any(w in text for w in ("forecast", "predict", "tomorrow", "next day", "horizon")):
            return "forecast"
        if any(
            w in text
            for w in (
                "anomal",
                "alert",
                "outlier",
                "fail",
                "critical",
                "deviation",
                "diagnostic",
            )
        ):
            return "diagnostic"
        return "analytics"

    def _build_context(self, df: pd.DataFrame, intent: str) -> str:
        kpis = get_kpis(df)
        lines = [
            "Stockhouse snapshot:",
            f"- total_tonnage={kpis.total_tonnage}",
            f"- total_batches={kpis.total_batches}",
            f"- avg_precision_pct={kpis.avg_precision_pct}",
            f"- avg_cycle_time_sec={kpis.avg_cycle_time_sec}",
        ]
        if intent in ("diagnostic", "forecast") and not df.empty:
            anomalies = get_anomalies(df).items[:8]
            if anomalies:
                lines.append("Recent out-of-tolerance batches:")
                for item in anomalies:
                    lines.append(
                        f"- {item.batch_id} hopper={item.hopper_id} "
                        f"dev={item.deviation_pct}% ({item.reason})"
                    )
        return "\n".join(lines)

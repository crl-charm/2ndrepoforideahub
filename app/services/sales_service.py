from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import Any, Optional

from app import socketio
from app.core.interfaces import Clock
from app.repositories.sales_repository import SalesRepository


@dataclass(frozen=True)
class SalesService:
    repo: SalesRepository
    clock: Clock = None

    @staticmethod
    def _shape(summary_row: Any) -> dict[str, Any]:
        return {
            "transactions": int(summary_row.transactions or 0),
            "total_revenue": float(summary_row.total_revenue or 0),
            "space_revenue": float(summary_row.space_revenue or 0),
            "food_revenue": float(summary_row.food_revenue or 0),
        }

    def daily_sales(self) -> dict[str, Any]:
        today = self.clock.now().date()
        return {"date": str(today), **self._shape(self.repo.summary_for_day(today))}

    def sales_summary(self, period: str) -> dict[str, Any]:
        today = self.clock.now().date()
        if period == "yesterday":
            start_date = today - timedelta(days=1)
            end_date = start_date
        elif period == "7days":
            start_date = today - timedelta(days=6)
            end_date = today
        elif period == "1month":
            start_date = today - timedelta(days=29)
            end_date = today
        else:
            period = "today"
            start_date = today
            end_date = today
        return {
            "period": period,
            "start_date": str(start_date),
            "end_date": str(end_date),
            **self._shape(self.repo.summary_for_range(start_date, end_date)),
        }

    def sales_compare(self) -> dict[str, Any]:
        today = self.clock.now().date()
        yesterday = today - timedelta(days=1)
        return {
            "today": self._shape(self.repo.summary_for_day(today)),
            "yesterday": self._shape(self.repo.summary_for_day(yesterday)),
            "last_7_days": self._shape(self.repo.summary_for_range(today - timedelta(days=6), today)),
            "last_30_days": self._shape(self.repo.summary_for_range(today - timedelta(days=29), today)),
        }

    def list_reports(self) -> list[dict[str, Any]]:
        reports = self.repo.list_reports()
        return [
            {
                "id": r.id,
                "report_date": r.report_date.strftime("%Y-%m-%d"),
                "total_revenue": float(r.total_revenue),
                "total_expenses": float(r.total_expenses),
                "net_balance": float(r.net_balance),
                "total_orders": r.total_orders,
                "total_sessions": r.total_sessions,
                "generated_by": r.generated_by_user.username if r.generated_by_user else "Unknown",
                "notes": r.notes,
            }
            for r in reports
        ]

    def generate_report(
        self,
        report_date: date,
        generated_by: int,
        notes: Optional[str],
    ) -> dict[str, Any]:
        transactions = self.repo.get_daily_transactions(report_date)
        orders = self.repo.get_daily_orders(report_date)
        sessions = self.repo.get_daily_sessions(report_date)

        total_revenue = Decimal("0")
        for tx in transactions:
            if tx.total_bill:
                total_revenue += Decimal(str(tx.total_bill))

        total_expenses = Decimal("0")

        net_balance = total_revenue - total_expenses

        report = self.repo.create_report(
            report_date=report_date,
            total_revenue=total_revenue,
            total_expenses=total_expenses,
            net_balance=net_balance,
            total_orders=len(orders),
            total_sessions=len(sessions),
            generated_by=generated_by,
            notes=notes,
        )
        self.repo.save()

        socketio.emit(
            "daily_sales_closed",
            {
                "report_date": report_date.strftime("%Y-%m-%d"),
                "total_revenue": float(total_revenue),
                "net_balance": float(net_balance),
            },
        )

        return {
            "success": True,
            "data": {
                "id": report.id,
                "report_date": report_date.strftime("%Y-%m-%d"),
                "total_revenue": float(total_revenue),
                "total_expenses": float(total_expenses),
                "net_balance": float(net_balance),
            },
        }

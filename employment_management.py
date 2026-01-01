from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime, date
from typing import Dict, List, Optional


@dataclass
class Employee:
    """Basic information for an employee record."""

    id: int
    name: str
    department: str
    role: str


@dataclass
class AttendanceRecord:
    """Represents a single shift for an employee."""

    employee_id: int
    clock_in: str
    clock_out: Optional[str] = None

    def is_open(self) -> bool:
        return self.clock_out is None

    def close(self) -> None:
        if self.clock_out is not None:
            raise ValueError("Shift already closed")
        self.clock_out = datetime.now().isoformat(timespec="seconds")


class EmploymentManager:
    """Simple JSON-backed employment management system."""

    def __init__(self, data_path: str = "data/employees.json") -> None:
        self.data_path = data_path
        self._state: Dict[str, List[Dict]] = {"employees": [], "attendance": []}
        self._load()

    # Persistence helpers -------------------------------------------------
    def _load(self) -> None:
        if not os.path.exists(self.data_path):
            os.makedirs(os.path.dirname(self.data_path) or ".", exist_ok=True)
            self._state = {"employees": [], "attendance": []}
            return

        with open(self.data_path, "r", encoding="utf-8") as fp:
            self._state = json.load(fp)

    def _save(self) -> None:
        os.makedirs(os.path.dirname(self.data_path) or ".", exist_ok=True)
        with open(self.data_path, "w", encoding="utf-8") as fp:
            json.dump(self._state, fp, indent=2, ensure_ascii=False)

    # Employee management -------------------------------------------------
    def list_employees(self) -> List[Employee]:
        return [Employee(**e) for e in self._state.get("employees", [])]

    def add_employee(self, name: str, department: str, role: str) -> Employee:
        employees = self._state.setdefault("employees", [])
        next_id = 1 + max((emp["id"] for emp in employees), default=0)
        employee = Employee(id=next_id, name=name, department=department, role=role)
        employees.append(asdict(employee))
        self._save()
        return employee

    def find_employee(self, employee_id: int) -> Optional[Employee]:
        for raw in self._state.get("employees", []):
            if raw["id"] == employee_id:
                return Employee(**raw)
        return None

    # Attendance management ----------------------------------------------
    def _open_record(self, employee_id: int) -> Optional[AttendanceRecord]:
        for raw in self._state.get("attendance", []):
            if raw["employee_id"] == employee_id and raw.get("clock_out") is None:
                return AttendanceRecord(**raw)
        return None

    def clock_in(self, employee_id: int) -> AttendanceRecord:
        if not self.find_employee(employee_id):
            raise ValueError(f"Employee {employee_id} does not exist")

        if self._open_record(employee_id):
            raise ValueError(f"Employee {employee_id} is already clocked in")

        record = AttendanceRecord(
            employee_id=employee_id, clock_in=datetime.now().isoformat(timespec="seconds")
        )
        self._state.setdefault("attendance", []).append(asdict(record))
        self._save()
        return record

    def clock_out(self, employee_id: int) -> AttendanceRecord:
        for raw in self._state.get("attendance", []):
            if raw["employee_id"] == employee_id and raw.get("clock_out") is None:
                record = AttendanceRecord(**raw)
                record.close()
                raw["clock_out"] = record.clock_out
                self._save()
                return record
        raise ValueError(f"Employee {employee_id} has no open shift")

    def report_for_date(self, target: Optional[date] = None) -> List[AttendanceRecord]:
        target = target or date.today()
        results: List[AttendanceRecord] = []
        for raw in self._state.get("attendance", []):
            clock_in_date = datetime.fromisoformat(raw["clock_in"]).date()
            if clock_in_date == target:
                results.append(AttendanceRecord(**raw))
        return results


__all__ = ["EmploymentManager", "Employee", "AttendanceRecord"]

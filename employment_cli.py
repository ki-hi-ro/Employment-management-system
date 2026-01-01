import argparse
from datetime import datetime
from typing import Optional

from employment_management import EmploymentManager


def _print_employee(employee) -> None:
    print(f"[{employee.id}] {employee.name} ({employee.department} / {employee.role})")


def _print_attendance(record, indent: str = "") -> None:
    status = "open" if record.clock_out is None else record.clock_out
    print(f"{indent}Employee {record.employee_id}: {record.clock_in} -> {status}")


def handle_add_employee(args: argparse.Namespace, manager: EmploymentManager) -> None:
    employee = manager.add_employee(args.name, args.department, args.role)
    print("Employee registered:")
    _print_employee(employee)


def handle_list(args: argparse.Namespace, manager: EmploymentManager) -> None:
    employees = manager.list_employees()
    if not employees:
        print("No employees registered yet.")
        return

    for employee in employees:
        _print_employee(employee)


def handle_clock_in(args: argparse.Namespace, manager: EmploymentManager) -> None:
    record = manager.clock_in(args.employee_id)
    print("Clock-in recorded:")
    _print_attendance(record)


def handle_clock_out(args: argparse.Namespace, manager: EmploymentManager) -> None:
    record = manager.clock_out(args.employee_id)
    print("Clock-out recorded:")
    _print_attendance(record)


def handle_report(args: argparse.Namespace, manager: EmploymentManager) -> None:
    target: Optional[str] = args.date
    parsed_date = None
    if target:
        parsed_date = datetime.strptime(target, "%Y-%m-%d").date()
    records = manager.report_for_date(parsed_date)
    if not records:
        print("No records for the selected date.")
        return

    print(f"Attendance for {parsed_date or 'today'}:")
    for record in records:
        _print_attendance(record, indent="  ")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Employment management CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add = subparsers.add_parser("add-employee", help="Register a new employee")
    add.add_argument("name", help="Full name of the employee")
    add.add_argument("department", help="Department name")
    add.add_argument("role", help="Role or title")
    add.set_defaults(func=handle_add_employee)

    list_parser = subparsers.add_parser("list", help="List all employees")
    list_parser.set_defaults(func=handle_list)

    clock_in = subparsers.add_parser("clock-in", help="Clock an employee in")
    clock_in.add_argument("employee_id", type=int, help="Employee id")
    clock_in.set_defaults(func=handle_clock_in)

    clock_out = subparsers.add_parser("clock-out", help="Clock an employee out")
    clock_out.add_argument("employee_id", type=int, help="Employee id")
    clock_out.set_defaults(func=handle_clock_out)

    report = subparsers.add_parser("report", help="Show attendance for a date")
    report.add_argument("--date", help="Target date in YYYY-MM-DD format")
    report.set_defaults(func=handle_report)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    manager = EmploymentManager()
    args.func(args, manager)


if __name__ == "__main__":
    main()

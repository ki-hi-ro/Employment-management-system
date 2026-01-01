# Employment Management System

A lightweight, file-based employment management CLI for registering employees and tracking daily attendance.

## Features
- Register employees with department and role information.
- List all employees.
- Clock employees in and out with timestamps.
- View attendance records for today or a specific date.

## Getting started
This tool only relies on the Python standard library. Use Python 3.10+.

```bash
python employment_cli.py --help
```

### Register an employee
```bash
python employment_cli.py add-employee "Alice Example" Sales "Account Manager"
```

### List employees
```bash
python employment_cli.py list
```

### Clock in / Clock out
```bash
python employment_cli.py clock-in 1
python employment_cli.py clock-out 1
```

### Attendance report
Show today's attendance:
```bash
python employment_cli.py report
```

Or for a specific date:
```bash
python employment_cli.py report --date 2024-08-01
```

Employee and attendance data are stored at `data/employees.json` in JSON format for easy portability.

from __future__ import annotations

import json
import mimetypes
from dataclasses import asdict
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional
from urllib.parse import parse_qs, urlparse

from employment_management import EmploymentManager


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


class EmploymentWebHandler(BaseHTTPRequestHandler):
    manager = EmploymentManager(str(BASE_DIR / "data" / "employees.json"))

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/employees":
            self._send_json([asdict(employee) for employee in self.manager.list_employees()])
            return

        if path == "/api/report":
            query = parse_qs(parsed.query)
            target = None
            if query.get("date", [""])[0]:
                try:
                    target = datetime.strptime(query["date"][0], "%Y-%m-%d").date()
                except ValueError:
                    self._send_error("Date must be in YYYY-MM-DD format", HTTPStatus.BAD_REQUEST)
                    return
            records = [asdict(record) for record in self.manager.report_for_date(target)]
            self._send_json(records)
            return

        self._serve_static(path)

    def do_HEAD(self) -> None:
        self._serve_static(urlparse(self.path).path, include_body=False)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        payload = self._read_json()
        if payload is None:
            return

        try:
            if parsed.path == "/api/employees":
                employee = self.manager.add_employee(
                    self._required(payload, "name"),
                    self._required(payload, "department"),
                    self._required(payload, "role"),
                )
                self._send_json(asdict(employee), HTTPStatus.CREATED)
                return

            if parsed.path == "/api/clock-in":
                record = self.manager.clock_in(int(self._required(payload, "employee_id")))
                self._send_json(asdict(record), HTTPStatus.CREATED)
                return

            if parsed.path == "/api/clock-out":
                record = self.manager.clock_out(int(self._required(payload, "employee_id")))
                self._send_json(asdict(record))
                return
        except ValueError as exc:
            self._send_error(str(exc), HTTPStatus.BAD_REQUEST)
            return

        self._send_error("Not found", HTTPStatus.NOT_FOUND)

    def log_message(self, format: str, *args) -> None:
        print(f"{self.address_string()} - {format % args}")

    def _serve_static(self, path: str, include_body: bool = True) -> None:
        if path == "/":
            path = "/index.html"

        requested = (STATIC_DIR / path.lstrip("/")).resolve()
        if not requested.is_relative_to(STATIC_DIR) or not requested.is_file():
            self._send_error("Not found", HTTPStatus.NOT_FOUND)
            return

        content_type = mimetypes.guess_type(requested.name)[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(requested.stat().st_size))
        self.end_headers()
        if include_body:
            with requested.open("rb") as fp:
                self.wfile.write(fp.read())

    def _read_json(self) -> Optional[dict]:
        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length).decode("utf-8")
            return json.loads(raw or "{}")
        except json.JSONDecodeError:
            self._send_error("Invalid JSON", HTTPStatus.BAD_REQUEST)
            return None

    def _required(self, payload: dict, key: str) -> str:
        value = str(payload.get(key, "")).strip()
        if not value:
            raise ValueError(f"{key} is required")
        return value

    def _send_json(self, body: object, status: HTTPStatus = HTTPStatus.OK) -> None:
        encoded = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _send_error(self, message: str, status: HTTPStatus) -> None:
        self._send_json({"error": message}, status)


def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), EmploymentWebHandler)
    print(f"Employment management web app running at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()

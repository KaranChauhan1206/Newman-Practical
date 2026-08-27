#!/usr/bin/env python3
# Mock MCP-style schedule_agent server for the Newman/Postman take-home exercise.
# No dependencies beyond the Python 3 standard library.

import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = 8765
VALID_CANCEL_ID = "CNF-1001"

sessions = {}


def envelope(request_id, status, action, message, details=None):
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "content": [{"type": "text", "text": message}],
            "structuredContent": {
                "result": {
                    "status": status,
                    "action": action,
                    "message": message,
                    "details": details or {},
                }
            },
        },
    }


def handle_request(session_id, request_id, arguments):
    text = (arguments.get("user_request") or "").lower()
    state = sessions.setdefault(session_id, {"stage": "new"})

    if "cancel" in text:
        match = re.search(r"cnf-\d+", text)
        conf_id = match.group(0).upper() if match else None
        if conf_id == VALID_CANCEL_ID:
            return envelope(
                request_id, "complete", "cancel_appointment",
                f"Your appointment {conf_id} has been cancelled.",
                {"confirmation_id": conf_id},
            )
        return envelope(
            request_id, "error", "cancel_appointment",
            f"No appointment found matching {conf_id or 'the confirmation number you provided'}.",
            {"confirmation_id": conf_id},
        )

    if state["stage"] == "awaiting_confirmation":
        if "yes" in text or "confirm" in text:
            state["stage"] = "booked"
            return envelope(
                request_id, "complete", "create_appointment",
                f"You're booked for {state['proposed_time']}. Confirmation: CNF-2001.",
                {"confirmation_id": "CNF-2001", "selected_datetime": state["proposed_time"]},
            )
        state["stage"] = "new"

    if "oil change" in text and re.search(r"\d{1,2}(:\d{2})?\s*(am|pm)", text):
        state["stage"] = "awaiting_confirmation"
        state["proposed_time"] = "Tuesday at 9:00 AM"
        return envelope(
            request_id, "awaiting_input", "create_appointment",
            "I'd like to confirm - do you want the Tuesday 9:00 AM slot for your oil change?",
            {"needed_info": ["timeslot_confirmation"]},
        )

    return envelope(
        request_id, "awaiting_input", "create_appointment",
        "I can help with that - which vehicle and what service do you need?",
        {"needed_info": ["vehicle_confirmation", "service"]},
    )


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw or b"{}")
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            return

        session_id = self.headers.get("mcp-session-id", "no-session")
        request_id = body.get("id", 1)
        arguments = body.get("params", {}).get("arguments", {})

        response = handle_request(session_id, request_id, arguments)

        payload = json.dumps(response).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        payload = b"Mock schedule_agent server is running. POST to /mcp.\n"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    server = ThreadingHTTPServer(("localhost", PORT), Handler)
    print(f"Mock schedule_agent server running on http://localhost:{PORT}/mcp")
    print("Ctrl+C to stop.")
    server.serve_forever()

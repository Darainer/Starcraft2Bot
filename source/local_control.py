"""Single-command, session-scoped mailbox for the running assistant."""

import json
import os
import tempfile
from pathlib import Path


def queue_command(report_path, command):
    report_path = Path(report_path).resolve(strict=True)
    report = json.loads(report_path.read_text(encoding="utf-8-sig"))
    if report.get("phase") not in {"bot_started", "observing"}:
        raise ValueError("Session is not running")
    if not report.get("local_control"):
        raise ValueError("Session predates local control; available after the next game launch")
    if not isinstance(command, str) or not command.startswith("!assist "):
        raise ValueError("Expected an !assist command")
    mailbox = report_path.with_suffix(".command.json")
    # Publish a complete file atomically without replacing an outstanding command.
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=mailbox.parent, delete=False) as stream:
        temporary = Path(stream.name)
        json.dump({"command": command}, stream)
    try:
        os.link(temporary, mailbox)
    finally:
        temporary.unlink()
    return mailbox


def consume_command(report_path, control, selected):
    mailbox = Path(report_path).with_suffix(".command.json")
    if not mailbox.exists():
        return None
    try:
        payload = json.loads(mailbox.read_text(encoding="utf-8"))
        command = payload["command"]
        if not isinstance(command, str) or not command.startswith("!assist "):
            raise ValueError("Expected an !assist command")
        if command.strip().lower() == "!assist quit":
            return {"command": command, "reply": "Leaving assistant match", "quit": True}
        return {"command": command, "reply": control.command(command, selected)}
    except (ValueError, KeyError, TypeError) as exc:
        return {"reply": f"Rejected mailbox command: {exc}"}
    finally:
        mailbox.unlink(missing_ok=True)

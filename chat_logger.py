import os
import sys
import threading
from datetime import datetime, timedelta

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')


def get_timestamp() -> str:
    """Return the current timestamp formatted for in-conversation messages."""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def get_date_string(dt: datetime | None = None) -> str:
    """Return the date formatted as YYYY-MM-DD."""
    if dt is None:
        dt = datetime.now()
    return dt.strftime('%Y-%m-%d')


def get_log_filename(script_path: str, date_str: str | None = None) -> str:
    """Generate daily log file path in logs/ named script_YYYY-MM-DD.log."""
    os.makedirs(LOG_DIR, exist_ok=True)
    base = os.path.splitext(os.path.basename(script_path))[0]
    if date_str is None:
        date_str = get_date_string()
    return os.path.join(LOG_DIR, f"{base}_{date_str}.log")


class ChatLogger:
    """Thread-safe daily logger that automatically rotates logs at midnight (00:00:00)."""

    def __init__(self, script_path: str):
        self.script_path = script_path
        self.base_name = os.path.splitext(os.path.basename(script_path))[0]
        self.lock = threading.Lock()
        self.current_date = get_date_string()
        self.filepath = get_log_filename(self.script_path, self.current_date)

        # Initialize today's log file with session start marker
        with self.lock, open(self.filepath, 'a', encoding='utf-8') as f:
            f.write(f"=== Session started at {get_timestamp()} [{self.base_name}] ===\n")

        self._schedule_midnight_rotation()

    def _schedule_midnight_rotation(self) -> None:
        """Schedule a background timer to close the log and open a new one at 00:00:00."""
        now = datetime.now()
        tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        delay = max(1.0, (tomorrow - now).total_seconds())

        timer = threading.Timer(delay, self._on_midnight)
        timer.daemon = True
        timer.start()

    def _on_midnight(self) -> None:
        """Handler triggered at 00:00:00 to rotate daily log files."""
        with self.lock:
            today = get_date_string()
            if today != self.current_date:
                self._rotate_to(today)
        self._schedule_midnight_rotation()

    def _rotate_to(self, new_date: str) -> None:
        """Close previous day's log file and start new daily log file."""
        prev_path = get_log_filename(self.script_path, self.current_date)
        try:
            with open(prev_path, 'a', encoding='utf-8') as f:
                f.write(f"=== Daily log closed at {self.current_date} 23:59:59 [{self.base_name}] ===\n")
        except OSError:
            pass

        self.current_date = new_date
        self.filepath = get_log_filename(self.script_path, new_date)
        try:
            with open(self.filepath, 'a', encoding='utf-8') as f:
                f.write(f"=== Daily log started at {get_timestamp()} [{self.base_name}] ===\n")
        except OSError:
            pass

    def _ensure_active_filepath(self) -> str:
        """Ensure the log file matches the current calendar day."""
        today = get_date_string()
        if today != self.current_date:
            self._rotate_to(today)
        return self.filepath

    def log(self, message: str, print_to_console: bool = True) -> None:
        """Log message to today's file and optionally to stdout."""
        clean_msg = message.rstrip('\r\n')
        if print_to_console:
            print(clean_msg)
        try:
            with self.lock:
                target_path = self._ensure_active_filepath()
                with open(target_path, 'a', encoding='utf-8') as f:
                    f.write(clean_msg + '\n')
        except OSError as e:
            print(f"[Logging Error] {e}", file=sys.stderr)

    def log_file_only(self, message: str) -> None:
        """Append message to today's log file without printing to stdout."""
        self.log(message, print_to_console=False)

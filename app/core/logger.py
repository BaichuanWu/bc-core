import json
import logging
import logging.handlers
import sys
from typing import Any, Optional

try:
    import sentry_sdk
    from sentry_sdk.integrations.logging import LoggingIntegration
except Exception:  # pragma: no cover - optional dependency
    sentry_sdk = None


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
            "lineno": record.lineno,
        }
        # include structured extras if provided
        extras = getattr(record, "extra", None)
        if isinstance(extras, dict):
            payload.update(extras)
        # include exception info if present
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logger(
    *,
    level: int = logging.INFO,
    log_to_stdout: bool = True,
    log_file: Optional[str] = None,
    when: str = "midnight",
    backup_count: int = 30,
    max_bytes: int = 0,
    use_json: bool = False,
    sentry_dsn: Optional[str] = None,
    sentry_level: int = logging.ERROR,
    service_name: Optional[str] = None,
):
    """Configure root logger for the application.

    - log_to_stdout: enable stdout StreamHandler
    - log_file: if provided, enable TimedRotatingFileHandler (when)
    - when: rotation interval for TimedRotatingFileHandler (e.g., 'midnight')
    - backup_count: how many rotated files to keep
    - max_bytes: if > 0 will use RotatingFileHandler with maxBytes instead of Timed
    - use_json: whether to emit JSON-formatted logs
    - sentry_dsn: optional DSN to initialize Sentry
    - sentry_level: events at/above this level will be captured by Sentry integration
    """

    root = logging.getLogger()
    root.setLevel(level)

    # remove existing handlers to avoid duplicate logs when reconfiguring
    for h in list(root.handlers):
        root.removeHandler(h)

    formatter: logging.Formatter
    if use_json:
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")

    if log_to_stdout:
        sh = logging.StreamHandler(sys.stdout)
        sh.setLevel(level)
        sh.setFormatter(formatter)
        root.addHandler(sh)

    if log_file:
        # choose file handler type
        if max_bytes and max_bytes > 0:
            fh = logging.handlers.RotatingFileHandler(
                log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
            )
        else:
            fh = logging.handlers.TimedRotatingFileHandler(
                log_file, when=when, backupCount=backup_count, encoding="utf-8"
            )
        fh.setLevel(level)
        fh.setFormatter(formatter)
        root.addHandler(fh)

    # configure Sentry if available and DSN provided
    if sentry_dsn and sentry_sdk:
        # capture logs of specified level and above as breadcrumbs / events
        sentry_logging = LoggingIntegration(
            level=logging.INFO,  # capture info and above as breadcrumbs
            event_level=sentry_level,  # send events when level >= sentry_level
        )
        sentry_sdk.init(dsn=sentry_dsn, integrations=[sentry_logging])


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def logger_exception(e: BaseException) -> Any:
    """Capture exception to Sentry if available, return sentry event id when possible."""
    if sentry_sdk:
        return sentry_sdk.capture_exception(e)
    # fallback: log exception to root logger
    logging.getLogger().exception("Captured exception (sentry not configured)")
    return None


__all__ = ["configure_logger", "get_logger", "logger_exception"]

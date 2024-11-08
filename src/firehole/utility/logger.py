import logging
import structlog
import sys

from firehole.utility import settings


processors = [
    structlog.processors.add_log_level,
    structlog.processors.TimeStamper(fmt="iso", utc=True),
]
if sys.stderr.isatty() and settings.DEBUG:  # Only for debugging in a local terminal
    processors += [structlog.dev.ConsoleRenderer()]
else:
    processors += [structlog.processors.JSONRenderer()]

structlog.configure(
    processors=processors,
    wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG if settings.DEBUG else logging.INFO),
)

logger: structlog.stdlib.BoundLogger = structlog.get_logger("firehole")

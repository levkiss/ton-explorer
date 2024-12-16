import structlog
import logging

def setup_logging():
    logging.basicConfig(
        format="%(message)s",
        level=logging.INFO,
    )
    
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
    )

logger = structlog.get_logger()
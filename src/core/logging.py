import logging
import sys
import structlog

def setup_logging(debug: bool = True):
    log_level = logging.DEBUG if debug else logging.INFO

    shared_processors = [
        structlog.contextvars.merge_contextvars,          
        structlog.stdlib.add_logger_name,                 
        structlog.stdlib.add_log_level,                
        structlog.stdlib.PositionalArgumentsFormatter(), 
        structlog.processors.TimeStamper(fmt="iso"),      
        structlog.processors.StackInfoRenderer(),        
        structlog.processors.format_exc_info,            
        structlog.processors.UnicodeDecoder(),
    ]

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level
    )

    if debug:
        renderer = structlog.dev.ConsoleRenderer(colors=True)
    else:
        renderer = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=shared_processors + [
            renderer,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
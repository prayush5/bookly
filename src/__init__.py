from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.books.routes import book_router
from contextlib import asynccontextmanager
from src.db.main import init_db
from src.auth.routes import auth_router
from src.errors import BooklyException
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from src.core.logging import setup_logging
import structlog, time

from src.middleware import limiter
import uuid

setup_logging(debug=True)

logger = structlog.get_logger(__name__)

@asynccontextmanager
async def life_span(app:FastAPI):
    logger.info("Server has started ...", status="running", version="v1")
    await init_db()
    yield
    logger.info("Server has been stopped")

app = FastAPI(
    title="Bookly",
    description="REST API for book web service",
    lifespan=life_span
    )

@app.middleware("http")
async def log_requests(request: Request, call_next):
    structlog.contextvars.clear_contextvars()
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    structlog.contextvars.bind_contextvars(request_id=request_id)

    start_time = time.perf_counter()

    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception as exc:
        process_time = time.perf_counter() - start_time
        logger.exception(
            "http_request_failed",
            method=request.method,
            path=request.url.path,
            duration=f"{process_time:.4f}s",
            error=str(exc)
        )
        raise exc
    
    process_time = time.perf_counter() - start_time
    response.headers["X-Request-ID"] = request_id

    if response.status_code >= 500:
        log_fn = logger.error
    elif response.status_code >= 400:
        log_fn = logger.warning
    else:
        log_fn = logger.info
    
    log_fn(
        "http_request",
        method=request.method,
        path=request.url.path,
        status_code=status_code,
        duration=f"{process_time:.4f}s",
    )

    return response

app.state.limiter=limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(book_router, prefix=f"/api/v1/books", tags=['books'])
app.include_router(auth_router, prefix=f"/api/v1/auth", tags=['auth'])

@app.exception_handler(BooklyException)
async def bookly_exception_handler(
    request: Request,
    exc: BooklyException
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message
        }
    )
import os
import time
import uuid
import socket
import logging
import collections
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, Header, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
import httpx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger('api-gateway')

API_KEY = os.getenv("API_KEY", "validus-secret-key")
ML_SERVICE_URL = os.getenv("ML_SERVICE_URL", "http://localhost:5000")
SHARED_UPLOAD_DIR = Path(os.getenv("SHARED_UPLOAD_DIR", "/shared/uploads"))

# ---------------------------------------------------------------------------
# Rate Limiter (in-memory, per IP)
# ---------------------------------------------------------------------------
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "10"))   # max requests
RATE_LIMIT_WINDOW   = int(os.getenv("RATE_LIMIT_WINDOW", "60"))     # per N seconds

# Maps IP -> deque of request timestamps within the current window
_request_log: dict[str, collections.deque] = collections.defaultdict(collections.deque)

# ---------------------------------------------------------------------------
# Lifespan (replaces deprecated @app.on_event("startup") / "shutdown")
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────────────────────────
    SHARED_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Upload directory ready: {SHARED_UPLOAD_DIR}")
    logger.info("Validus API Gateway started")

    yield  # Application runs here

    # ── Shutdown ─────────────────────────────────────────────────────────────
    logger.info("Validus API Gateway shutting down")


app = FastAPI(
    title="Validus API Gateway",
    description="Public-facing gateway for signature verification",
    version="1.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Rate Limiting Middleware
# ---------------------------------------------------------------------------
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Pass through health checks without rate limiting
    if request.url.path in ("/health", "/docs", "/openapi.json"):
        return await call_next(request)

    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW

    # Purge timestamps outside the current window
    timestamps = _request_log[client_ip]
    while timestamps and timestamps[0] < window_start:
        timestamps.popleft()

    if len(timestamps) >= RATE_LIMIT_REQUESTS:
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        return JSONResponse(
            status_code=429,
            content={
                "error": "Too Many Requests",
                "detail": f"Limit is {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW}s."
            }
        )

    timestamps.append(now)
    return await call_next(request)


# ---------------------------------------------------------------------------
# Global Exception Handler
# ---------------------------------------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

# ---------------------------------------------------------------------------
# API Key dependency
# ---------------------------------------------------------------------------
async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key

# Allowed image MIME types
ALLOWED_IMG_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/bmp", "image/tiff", "image/webp"}

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.post("/api/verify", dependencies=[Depends(verify_api_key)])
async def verify_signatures(
    reference: UploadFile = File(...),
    query: UploadFile = File(...),
):
    """
    Public endpoint for signature verification.
    1. Validates image types
    2. Saves to shared volume with UUID filenames
    3. Calls ML service with file paths
    4. Cleans up files
    5. Returns verdict
    """

    # 1. Validate MIME types
    if reference.content_type not in ALLOWED_IMG_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid reference image type: {reference.content_type}")
    if query.content_type not in ALLOWED_IMG_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid query image type: {query.content_type}")

    # 2. Generate unique filenames and save to shared volumes
    request_id = str(uuid.uuid4())
    ref_path   = SHARED_UPLOAD_DIR / f"{request_id}_ref.png"
    query_path = SHARED_UPLOAD_DIR / f"{request_id}_query.png"

    try:
        ref_path.write_bytes(await reference.read())
        query_path.write_bytes(await query.read())
        logger.info(f"[{request_id}] Files saved to shared volume")

        # 3. Call ML service with file paths
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{ML_SERVICE_URL}/process-internal",
                json={"ref_path": str(ref_path), "query_path": str(query_path)},
            )

        # 4. Handle ML service errors
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"ML service error: {response.text}"
            )

        result = response.json()
        logger.info(f"[{request_id}] Verdict: {result['verdict']}")
        return result

    finally:
        # 5. Always clean up files from shared volume
        for path in (ref_path, query_path):
            if path.exists():
                path.unlink()
        logger.info(f"[{request_id}] Cleaned up files from shared volume")


@app.get("/health")
async def health_check():
    return {"status": "ok", "instance": socket.gethostname()}
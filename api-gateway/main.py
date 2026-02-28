import os
import uuid
import socket
import logging
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Header, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
import httpx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger('api-gateway')

API_KEY = os.getenv("API_KEY", "validus-secret-key")
ML_SERVICE_URL= os.getenv("ML_SERVICE_URL", "http://localhost:5000")
SHARED_UPLOAD_DIR = Path(os.getenv("SHARED_UPLOAD_DIR", "/shared/uploads"))

app = FastAPI(
    title="Validus API Gateway",
    description="Public-facing gateway for signature verification",
    version="1.0.0"
)

# Ensure upload directory exists on startup
@app.on_event("startup")
async def startup_event():
    SHARED_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Upload directory ready: {SHARED_UPLOAD_DIR}")
    
# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request:Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

# API Key validation
async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key

# Allowed image MIME types
ALLOWED_IMG_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/bmp", "image/tiff", "image/webp"}

# Endpoints
@app.post("/api/verify", dependencies=[Depends(verify_api_key)])
async def verify_signatures(
    reference: UploadFile = File(...),
    query: UploadFile = File(...)
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
    ref_filename = f"{request_id}_ref.png"
    query_filename = f"{request_id}_query.png"
    
    ref_path = SHARED_UPLOAD_DIR / ref_filename
    query_path = SHARED_UPLOAD_DIR / query_filename
    
    try:
        ref_content = await reference.read()
        query_content = await query.read()
        
        ref_path.write_bytes(ref_content)
        query_path.write_bytes(query_content)
        
        logger.info(f"[{request_id}] Files saved to shared volume")
        
        # 3. Call ML service with file paths
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{ML_SERVICE_URL}/process-internal", json={
                "ref_path": str(ref_path),
                "query_path": str(query_path)
            })
        # 4 Handle ML service errors
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"ML service error: {response.text}")
        
        result = response.json()
        logger.info(f"[{request_id}] Verdict: {result['verdict']}")
        
        return result
    finally:
        # 5. Always clean up files from shared volumes
        if ref_path.exists():
            ref_path.unlink()
        if query_path.exists():
            query_path.unlink()
        
        logger.info(f"[{request_id}] Cleaned up files from shared volumes")
        
@app.get("/health")
async def health_check():
    return {"status": "ok", "instance": socket.gethostname()} # Returns the hostname of the machine where the API is running
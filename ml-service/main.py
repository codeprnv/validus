import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from preprocessor import ImagePipeline
from verifier import SignatureVerifier

# Initialize logging 
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ml-service")

# Fastapi app
app = FastAPI(
    title = "Validus ML Service",
    description = "Internal CV microservice for signature verification",
    version = "1.0.0"
)

pipeline = ImagePipeline()
verifier = SignatureVerifier()

# Pydantic models
class VerifyRequest(BaseModel):
    ref_path: str
    query_path: str

class VerifyResponse(BaseModel):
    verdict: str
    confidence: float
    is_match: bool

# Endpoints
@app.post("/process-internal", response_model=VerifyResponse)

async def process_internal(body: VerifyRequest):
    """ 
    Accepts file path from the shared volume, 
    runs the SSIM verification pipeline, returns the verdict.
    """
    logger.info(f"Processing - ref: {body.ref_path}, query: {body.query_path}")
    
    ref_img = pipeline.process(body.ref_path)
    query_img = pipeline.process(body.query_path)
    
    if ref_img is None:
        raise HTTPException(status_code=400, detail=f"Failed to process reference image: {body.ref_path}")
    if query_img is None:
        raise HTTPException(status_code=400,detail=f"Failed to process query image: {body.query_path}")
    
    # Run SSIM verification
    result = verifier.verify(ref_img, query_img)
    
    return VerifyResponse(
        verdict = result["verdict"],
        confidence= result["similarity_score"],
        is_match = result["pass"]
    )
    
@app.get("/health")
async def health_check():
    return {"status": "ok"}
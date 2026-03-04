import logging
import argparse
from ml_service.preprocessor import ImagePipeline
from ml_service.verifier import SignatureVerifier
from src.utils import visualize_forensic_dashboard
import ml_service.config
import os
from dotenv import load_dotenv

load_dotenv()

# Setup Logging
logging.basicConfig(level=ml_service.config.LOG_LEVEL, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("SignatureSystem")

def main(ref_path, query_path):
    logger.info(f"-----Starting Signature Verification System -----")

    # 1. Initialize Modules
    pipeline = ImagePipeline()
    verifier = SignatureVerifier()

    # 2. Process Image
    logger.info(f"Processing Reference: {ref_path}")
    ref_img, ref_debug = pipeline.process(ref_path, debug=True)

    logger.info(f"Processing Query: {query_path}")
    query_img, query_debug = pipeline.process(query_path, debug=True)

    if ref_img is None or query_img is None:
        logger.error('Pipeline aborted due to image errors!')
        return

    # 3. Verify
    result = verifier.verify(ref_img, query_img)

    # 4. Final Output
    print("\n" + "="*30)
    print(f"Final Result: {result['verdict']}")
    print(f"Confidence: {result['similarity_score']}%")
    print(f"Status: {'✅ Match' if result['pass'] else '❌ Not Match'}")
    print("="*30 + "\n")

#     5. Visualization
    logger.info("Generating forensic dashboard....")

    visualize_forensic_dashboard(ref_debug, query_debug, result['diff_map'], result)

def resolve_inputs():
    parser = argparse.ArgumentParser(description="Signature Verification System")
    
    parser.add_argument("--ref", required=False)
    parser.add_argument("--query", required=False)
    
    args = parser.parse_args()
    
    ref = args.ref or os.getenv("REF_IMAGE")
    query = args.query or os.getenv("QUERY_IMAGE")
    
    if not ref or not query:
        raise RuntimeError("Input paths must be provided via CLI (--ref, --query)"
        "or environment variables (REF_IMAGE, QUERY_IMAGE)")
    return ref, query

if __name__ == "__main__":
    ref_path, query_path = resolve_inputs()
    main(ref_path, query_path)
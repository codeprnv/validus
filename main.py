import logging
import argparse
from src.preprocessor import ImagePipeline
from src.verifier import SignatureVerifier
from src.utils import visualize_forensic_dashboard
import config


# Setup Logging
logging.basicConfig(level=config.LOG_LEVEL, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
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
    print(f"Final Result: {result["verdict"]}")
    print(f"Confidence: {result["similarity_score"]}%")
    print(f"Status: {"✅ Match" if result['pass'] else "❌ Not Match"}")
    print("="*30 + "\n")

#     5. Visualization
    logger.info("Generating forensic dashboard....")

    visualize_forensic_dashboard(ref_debug, query_debug, result['diff_map'], result)

if __name__ == "__main__":
    # Allows running from command line: python main.py --ref img1.png --query img2.png
    parser = argparse.ArgumentParser(description="Offline Signature Verification")
    parser.add_argument("--ref", required=True, help="Path to reference signature")
    parser.add_argument("--query", required=True, help="Path to query signature")

    args = parser.parse_args()
    main(args.ref, args.query)
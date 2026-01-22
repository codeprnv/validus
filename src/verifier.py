import logging
from skimage.metrics import structural_similarity as ssim
import numpy as np
from typing import Dict, Any
from config import SSIM_THRESHOLD

class SignatureVerifier:
    """
    Engine for comparing two pre-processed images.
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def verify(self, ref_img:np.ndarray, query_img:np.ndarray) -> Dict[str, Any]:
        """
        Compares References Vs Query.
        :param ref_img:
        :param query_img:
        :return: Dictionary with score, verdict, and metadata
        """
        # 1. Structural Similarity index (SSIM)
        # win_size=7 is standard for small structural textures
        score, diff_map = ssim(ref_img, query_img, full=True, win_size=7)

        # 2. Make Decision
        is_genuine = score >= SSIM_THRESHOLD

        result = {
            "similarity_score": round(score * 100, 2),
            "diff_map": diff_map,
            "verdict": "GENUINE" if is_genuine else "FORGED",
            "threshold_used": SSIM_THRESHOLD,
            "pass": is_genuine
        }

        self.logger.info(f"Verification Complete: {result['verdict']} ({result['similarity_score']}%)")
        return result
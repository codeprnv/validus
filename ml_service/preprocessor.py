import cv2
import numpy as np
import logging
from typing import Optional, Any;

from cv2 import UMat
from numpy import dtype, ndarray

from ml_service.config import TARGET_SIZE


class ImagePipeline:
    """ Production pipeline for normalizing signature images.
    Handles loading, grayscale conversion, and rigid resizing.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def process(self, image_path: str, debug=False) -> None | tuple[
        ndarray[tuple[Any, ...], dtype[Any]] | UMat | Any, dict[
            str, ndarray[tuple[Any, ...], dtype[Any]] | ndarray[tuple[Any, ...], Any] | UMat | Any]] | ndarray[
                                                           tuple[Any, ...], dtype[Any]] | UMat | Any:
        """ 
        Reads and normalizes an image.
        Returns: Processed numpy array or None if failure
        If debug=True, returns: (Final_Img, {Step_Images})
        """
        try:
            # 1. Load image
            img = cv2.imread(str(image_path))
            if img is None:
                self.logger.error(f'Failed to load image: {image_path}')
                return None
            # 2. Grayscale conversion
            if len(img.shape) == 3:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            else:
                gray = img
            # 3. Otsu's Binarization (Auto-thresholding)
            # Inverts logic so Ink = White, Paper = Black (better for processing)
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            # 4. Crop to content (bounding box)
            coords = cv2.findNonZero(binary)
            if coords is not None:
                x, y, w, h = cv2.boundingRect(coords)
                cropped = gray[y:y + h, x:x + w]
                binary_cropped = binary[y:y+h, x:x+w]
            else:
                cropped = gray  # fallback if image is blank
                binary_cropped = binary
            # 5. Rigid Resize
            final_img = cv2.resize(cropped, TARGET_SIZE)

            if debug:
                return final_img, {
                    "original": img,
                    "gray": gray,
                    "binary": binary_cropped,
                    "final": final_img
                }
            return final_img

        except Exception as e:
            self.logger.exception(f'Critical error processing {image_path}: {e}')
            return None

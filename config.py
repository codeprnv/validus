from pathlib import Path

# System settings
LOG_LEVEL= "INFO"

# Image processing
TARGET_SIZE = (300, 150) # (Width, height)
SIGMA_GAUSSIAN = 1.0 # For Noise Removal

# Decision Logic
SSIM_THRESHOLD = 0.80 # Score > 80% = Genuine
RATIO_TOLERANCE = 0.15 # Aspect ratio differences allowed (15%)

# Paths
DATA_DIR = Path('./data')
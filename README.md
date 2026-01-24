# VALIDUS 🛡️
> *Automated Forensic Signature Verification System*

**Validus** is a robust, production-ready computer vision pipeline designed to detect forged signatures. By leveraging advanced image preprocessing and Structural Similarity Index (SSIM) analysis, it provides definitive "Genuine" or "Forged" verdicts with high precision.

---

## 🚀 Key Features

*   **Production-Grade Pipeline**: Automated preprocessing chain (Grayscale → Otsu’s Binarization → Noise Removal → Rigid Cropping).
*   **Precision Verification**: Uses SSIM (Structural Similarity Index) for detecting subtle structural deviations.
*   **Dual Execution Mode**: Runs seamlessly via Docker containers or locally for development.
*   **Forensic Dashboard**: Generates visual debug outputs to analyze the verification process step-by-step.
*   **Zero-Config Defaults**: Works out-of-the-box with intelligent defaults, customizable via environment variables.

---

## 🛠️ Technical Architecture

Validus operates in two main stages:

### 1. The Preprocessing Engine
Raw images undergo a rigorous normalization process to ensure fair comparisons:
*   **Grayscale Conversion**: Eliminates color noise.
*   **Otsu's Binarization**: Automatically calculates the optimal threshold to separate ink from paper.
*   **ROI Extraction**: Detects the bounding box of the signature and crops tight to the ink.
*   **Rigid Resizing**: Standardizes all inputs to a fixed `300x150` resolution.

### 2. The Verification Core
The `SignatureVerifier` engine compares the normalized Reference vs. Query images using **SSIM**.
*   **Score > 80%**: ✅ **GENUINE** - The structural features match significantly.
*   **Score < 80%**: ❌ **FORGED** - Significant structural deviations detected.

*(Thresholds are configurable in `config.py`)*

---

## 📦 Getting Started

### Prerequisites
*   **Docker** (Recommended)
*   **Python 3.12+** (For local development)

### Environment Configuration
Validus uses environment variables to locate signature images. Create a `.env` file in the root directory:

```properties
# .env
REF_IMAGE=path/to/original_signature.png
QUERY_IMAGE=path/to/suspect_signature.png
```

---

## 🏃 Usage

### Option A: Docker (Recommended)
Build and run the containerized application. The output will be displayed in your terminal.

```bash
docker-compose up --build
```

### Option B: Local Execution
Install dependencies and run the script directly.

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run Verification**:
    *   **Using .env**:
        ```bash
        python main.py
        ```
    *   **Using CLI Arguments** (Overrides .env):
        ```bash
        python main.py --ref ./data/real.png --query ./data/fake.png
        ```

---

## 📊 Output Interpretation

The system outputs a clear verdict and a confidence score:

```text
==============================
Final Result: FORGED
Confidence: 45.32%
Status: ❌ Not Match
==============================
```

*   **Final Result**: The verdict (GENUINE / FORGED).
*   **Confidence**: The SSIM similarity percentage (0-100%).
*   **Status**: Quick visual indicator.

---

## 🔧 Configuration

Tweak the detection sensitivity in `config.py`:

| Constant | Default | Description |
| :--- | :--- | :--- |
| `SSIM_THRESHOLD` | `0.80` | Verification passing score (0 to 1). |
| `TARGET_SIZE` | `(300, 150)` | Resolution for normalized images. |
| `SIGMA_GAUSSIAN` | `1.0` | Strength of noise removal filter. |

---

## 📂 Project Structure

```text
validus/
├── src/
│   ├── preprocessor.py  # Image normalization pipeline
│   ├── verifier.py      # SSIM verification engine
│   └── utils.py         # Visualization tools
├── images/              # Test datasets
├── config.py            # System configuration
├── main.py              # Application entry point
├── Dockerfile           # Container definition
└── docker-compose.yml   # Docker orchestration
```

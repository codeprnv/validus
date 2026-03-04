# VALIDUS 🛡️

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![NGINX](https://img.shields.io/badge/NGINX-Load_Balanced-009639?style=for-the-badge&logo=nginx&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer_Vision-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-EC2_Deployed-FF9900?style=for-the-badge&logo=amazonwebservices&logoColor=white)

> **Enterprise-Grade Signature Forgery Detection System**

Validus is a containerized computer vision platform designed to detect forged signatures using automated preprocessing and similarity analysis. The system is architected as a scalable microservices ecosystem with an API Gateway, internal ML service, and load-balanced infrastructure optimized for production-style deployments.

It demonstrates real-world backend architecture patterns including reverse proxying, container orchestration, service isolation, and secure API design.

---

## 🚀 Key Features

| Feature | Description |
| :--- | :--- |
| **Microservices Architecture** | Decoupled services for infrastructure, API management, machine learning, and frontend UI. |
| **Production-Style CV Pipeline** | Grayscale conversion → Otsu's binarization → ROI extraction → SSIM comparison. |
| **NGINX Load Balancing** | Traffic distributed across multiple API Gateway replicas for improved scalability. |
| **Secure API Gateway** | All public endpoints protected via API Key authentication (`X-API-Key`). |
| **Stateless Web Interface** | Lightweight Gradio UI for uploading and verifying signatures. |
| **Containerized Infrastructure** | Docker Compose orchestrates all services with network isolation and shared volumes. |

---

## 🧠 System Architecture

```text
                    Client
                      │
                      ▼
        NGINX Reverse Proxy (HTTPS / 443)
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
   API Gateway    API Gateway    Frontend UI
   Replica 1      Replica 2      (Gradio)
   (FastAPI)      (FastAPI)
        │             │
        └──────┬──────┘
               ▼
     Internal ML Service
         (FastAPI)
               │
               ▼
   Computer Vision Pipeline
```

NGINX acts as the entry point, forwarding traffic to API Gateway replicas which coordinate signature verification tasks with the internal ML service.

---

## ⚙️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend** | Python, FastAPI, OpenCV, NumPy, scikit-image |
| **Infrastructure** | Docker, Docker Compose, NGINX, Cloudflare SSL |
| **Frontend** | Gradio |
| **Deployment** | AWS EC2 (Ubuntu), Containerized microservices |

---

## 🧠 Signature Verification Pipeline

The ML service performs a sequence of preprocessing and similarity evaluation steps:

1. Convert input signatures to **grayscale**
2. Apply **Otsu's thresholding** to binarize images
3. Extract the **Region of Interest** (ROI)
4. Normalize and align signature regions
5. Compute **Structural Similarity Index** (SSIM)
6. Compare similarity score against threshold to determine authenticity

---

## 📦 Quick Start (Local Development)

**Prerequisites:** Docker and Docker Compose

**1. Clone the Repository**
```bash
git clone https://github.com/codeprnv/validus.git
cd validus
```

**2. Create Environment File**

Create a `.env` file in the root directory:
```properties
API_KEY=validus-secret-key
ML_SERVICE_URL=http://ml-service:5000
API_GATEWAY_URL=http://api-gateway:8000/api/verify
```

**3. Start the System**
```bash
docker compose up --build
```

**Access the services:**
* **Web UI** → `http://localhost:8050`
* **API Docs** → `http://localhost/docs`

---

## ☁️ Deployment

Validus can be deployed to a cloud server (e.g., AWS EC2 Ubuntu instance) using Docker Compose.

```bash
git clone https://github.com/codeprnv/validus.git /opt/validus
cd /opt/validus
sudo bash deploy.sh
```

The deployment script installs Docker, builds containers, and launches the system.

---

## 🔌 API Usage

**Example Request:**
```bash
curl -X POST https://yourdomain.com/api/verify \
  -H "X-API-Key: validus-secret-key" \
  -F "reference=@original.png" \
  -F "query=@forged.png"
```

**Example Response:**
```json
{
  "verdict": "FORGED",
  "confidence": 45.32,
  "is_match": false
}
```

---

## 📂 Project Structure

```text
validus/
├── api-gateway/         # Public-facing REST API
├── frontend/            # Gradio Web Client
├── ml_service/          # Computer Vision Engine
│   ├── main.py          # Internal FastAPI endpoints
│   ├── config.py        # System configuration
│   ├── preprocessor.py  # Image normalization logic
│   └── verifier.py      # SSIM evaluation logic
├── infrastructure/      # NGINX & SSL configuration
├── docker-compose.yml   # Multi-container orchestration
└── deploy.sh            # Automated deployment script
```

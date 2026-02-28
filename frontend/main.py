import os
import gradio as gr
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("frontend")

# Read from environment variables, defaulting to internal Docker DNS
API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://nginx:80/api/verify")
API_KEY = os.getenv("API_KEY", "validus-secret-key")

def verify_signatures(ref_img, query_img):
    """
    Takes two image file paths from Gradio, sends them to the API Gateway using requests.
    """
    if not ref_img or not query_img:
        return "Error: Please upload both images.", 0.0

    logger.info(f"Sending verification request to {API_GATEWAY_URL}")

    try:
        # Build the multipart/form-data payload with the open file handles
        with open(ref_img, "rb") as ref_file, open(query_img, "rb") as query_file:
            files = {
                "reference": ("ref.png", ref_file, "image/png"),
                "query": ("query.png", query_file, "image/png")
            }
            headers = {"X-API-Key": API_KEY}
            
            response = requests.post(API_GATEWAY_URL, files=files, headers=headers)
            
            if response.status_code != 200:
                return f"API Error {response.status_code}: {response.text}", 0.0
                
            result = response.json()
            
            # Format the output beautifully for the UI
            verdict_text = f"{'✅' if result['is_match'] else '❌'} {result['verdict']}"
            return verdict_text, result['confidence']
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to connect to API Gateway: {e}")
        return f"Connection Error: Gateway might be down.", 0.0

# ──────────────────────────────────────────────
# Gradio Web Interface Layout
# ──────────────────────────────────────────────
with gr.Blocks(title="Validus Signature Verification", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🏦 Validus: Signature Verification")
    gr.Markdown("Upload a known reference signature and a questioned signature to verify authenticity via SSIM analysis. Powered by FastAPI Microservices.")
    
    with gr.Row():
        with gr.Column():
            ref_input = gr.Image(type="filepath", label="Reference Signature", height=250)
        with gr.Column():
            query_input = gr.Image(type="filepath", label="Questioned Signature", height=250)
            
    verify_btn = gr.Button("🔍 Verify Signatures", variant="primary")
    
    with gr.Row():
        verdict_output = gr.Textbox(label="Verdict", text_align="center", scale=2)
        confidence_output = gr.Number(label="Confidence Score (%)", scale=1)

    verify_btn.click(
        fn=verify_signatures,
        inputs=[ref_input, query_input],
        outputs=[verdict_output, confidence_output]
    )

if __name__ == "__main__":
    # In Docker, we bind to 0.0.0.0 and port 8050
    demo.launch(server_name="0.0.0.0", server_port=8050)

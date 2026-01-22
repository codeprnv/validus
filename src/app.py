import gradio as gr
import numpy as np
from src.preprocessor import ImagePipeline
from src.verifier import SignatureVerifier
import cv2

# Init System
pipeline = ImagePipeline()
verifier = SignatureVerifier()

def web_verify(ref_file, query_file):
    if ref_file is None or query_file is None:
        return "Error: Missing Image", 0.0, None

    # Process
    ref_img = pipeline.process(ref_file)
    query_img = pipeline.process(query_file)

    # Verify
    result = verifier.verify(ref_img, query_img)

    # Generate Heatmap for web
    diff = result["diff_map"]
    error_viz = (1 - diff) * 255
    heatmap = error_viz.astype(np.uint8)
    heatmap_color = cv2.applyColorMap(heatmap, cv2.COLORMAP_HOT)

    return result["verdict"], result["similarity_score"], heatmap_color

# Layout
interface = gr.Interface(
    fn=web_verify,
    inputs=[
        gr.Image(type="filepath", label="Reference Signature"),
        gr.Image(type="filepath", label="Questioned Signature")
    ],
    outputs=[
        gr.Textbox(label="Verdict"),
        gr.Number(label="Confidence Score (%)"),
        gr.Image(label="Structural Error Map")
    ],
    title="Validus",
    description="Deterministic Offline Signature Verification System",
    theme="default"
)

if __name__ == "__main__":
    interface.launch()
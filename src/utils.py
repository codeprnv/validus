import matplotlib.pyplot as plt
import numpy as np
import cv2
from matplotlib.backends.backend_pdf import PdfPages
import config

def visualize_forensic_dashboard(ref_data, query_data, diff_map, result, filename="Report.pdf"):
    """
    :param ref_data: Dicts from preprocessor with intermediate steps
    :param query_data: Dicts from preprocessor with intermediate steps
    :param diff_map:
    :param result:
    :param filename:
    :return: Generates a comprehensive 1-Page forensic report.
    """

    # Create a layout: 3 rows
    # Row 1: Preprocessing Pipeline
    # Row 2: Detailed Analysis
    # Row 3: Verdict & Confidence Meter

    fig = plt.figure(figsize=(15, 12), constrained_layout=True)
    gs = fig.add_gridspec(3, 1, height_ratios=[1, 1.5, 0.5])

    # Row 1: The pipeline
    r1 = gs[0].subgridspec(1, 4)
    ax1 = fig.add_subplot(r1[0])
    ax1.imshow(ref_data["binary"], cmap="gray")
    ax1.set_title("Reference (Binarized)")
    ax1.axis("off")

    ax2 = fig.add_subplot(r1[1])
    ax2.imshow(ref_data["final"], cmap="gray")
    ax2.set_title("Reference (Final)")
    ax2.axis("off")

    ax3 = fig.add_subplot(r1[2])
    ax3.imshow(query_data['binary'], cmap="gray")
    ax3.set_title("Query (Binarized)")
    ax3.axis("off")

    ax4 = fig.add_subplot(r1[3])
    ax4.imshow(query_data["final"], cmap="gray")
    ax4.set_title("Query (Final)")
    ax4.axis("off")

    # Row 2: The X-Ray Analysis
    r2 = gs[1].subgridspec(1, 3)

    # 1. Heatmap Overlay
    # Create a red overlay for differences
    error_viz = (1 - diff_map)
    heatmap_img = cv2.applyColorMap((error_viz * 255).astype(np.uint8), cv2.COLORMAP_JET)
    heatmap_img = cv2.cvtColor(heatmap_img, cv2.COLOR_BGR2RGB)

    # Blend Query Image with heatmap
    query_rgb = cv2.cvtColor(query_data["final"], cv2.COLOR_GRAY2RGB)
    overlay = cv2.addWeighted(query_rgb, 0.7, heatmap_img, 0.3 , 0)

    ax_ov = fig.add_subplot(r2[0])
    ax_ov.imshow(overlay)
    ax_ov.set_title("Forensic Overlay\n(Red = Deviation)")
    ax_ov.axis("off")

    # 2. Pure Difference Map
    ax_diff = fig.add_subplot(r2[1])
    im = ax_diff.imshow(error_viz, cmap="hot", vmin=0, vmax=1)
    ax_diff.axis('off')
    plt.colorbar(im, ax=ax_diff, fraction=0.046)

    # Row 3: The Verdict
    ax_meter = fig.add_subplot(gs[2])

    score = result["similarity_score"]
    threshold = config.SSIM_THRESHOLD * 100

    # Draw bar
    ax_meter.barh(0, 100, color="#f0f0f0", edgecolor="black", height= 0.5)

    # Color logic: Green if pass, Red if fail
    bar_color = "#2ecc71" if result["pass"] else "#e74c3c"
    ax_meter.barh(0, score, color=bar_color, edgecolor="black", height= 0.5)

    # Add threshold marker
    ax_meter.axvline(x=threshold, color="#f39c12", linewidth=4, linestyle="--")
    ax_meter.text(threshold, 0.6, f"Threshold ({threshold}%)", color="#f39c12", fontweight="bold")

    # Labels
    ax_meter.set_xlim(0, 100)
    ax_meter.set_yticks([])
    ax_meter.set_xlabel("Similarity Score (%)", fontsize=12)

    # Big Title
    verdict_text = f"VERDICT: {result["verdict"]} ({score}%)"
    ax_meter.text(50, -0.6, verdict_text, ha="center", va="top", fontsize=20, fontweight="bold", color=bar_color)

    # Save to PDF
    fig.suptitle("Validus Forensic Analysis Report", fontsize=24, fontweight="bold")
    plt.savefig(filename)
    print(f"📁 Report Saved to {filename}")
    plt.show()
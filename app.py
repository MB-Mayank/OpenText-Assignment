"""Gradio web app for AI-Powered Cloud Cost Optimizer.

This wraps the existing CLI pipeline so it can run on
Hugging Face Spaces: user enters a project description,
then sees the generated profile, billing JSON, full
optimization report JSON, and an interactive HTML report.
"""

import os
from typing import Any, Dict, List, Tuple

import gradio as gr

from llm_client import LLMClient
from profile_extractor import ProfileExtractor
from billing_generator import BillingGenerator
from cost_analyzer import CostAnalyzer
from html_report_generator import HTMLReportGenerator


OUTPUTS_DIR = "outputs"


def ensure_outputs_dir() -> None:
    os.makedirs(OUTPUTS_DIR, exist_ok=True)


def run_pipeline(description: str) -> Tuple[Dict[Any, Any], List[Dict[Any, Any]], Dict[Any, Any], str]:
    """Run the full cost-optimization pipeline for a description.

    Returns:
        profile_json, billing_json, report_json, html_report
    """
    description = (description or "").strip()
    if not description:
        raise gr.Error("Please enter a project description.")

    # Ensure output directory exists (important on Spaces)
    ensure_outputs_dir()

    # Initialize LLM-powered components
    llm = LLMClient()
    profile_extractor = ProfileExtractor(llm)
    billing_generator = BillingGenerator(llm)
    cost_analyzer = CostAnalyzer(llm)

    # 1) Extract project profile from natural language
    profile = profile_extractor.extract_profile(description)
    profile_extractor.validate_profile(profile)
    profile_extractor.save_profile(profile, os.path.join(OUTPUTS_DIR, "project_profile.json"))

    # 2) Generate synthetic billing from profile
    billing = billing_generator.generate_billing(profile)
    billing_generator.validate_billing(billing)
    billing_generator.save_billing(billing, os.path.join(OUTPUTS_DIR, "mock_billing.json"))

    # 3) Analyze costs and generate recommendations
    report = cost_analyzer.analyze_and_recommend(profile, billing)
    cost_analyzer.validate_report(report)
    cost_analyzer.save_report(report, os.path.join(OUTPUTS_DIR, "cost_optimization_report.json"))

    # 4) Generate rich HTML report
    html_path = os.path.join(OUTPUTS_DIR, "cost_optimization_report.html")
    HTMLReportGenerator.generate_html_report(profile, billing, report, html_path)

    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    return profile, billing, report, html_content


with gr.Blocks(title="AI Cloud Cost Optimizer") as demo:
    gr.Markdown(
        """
        # ☁️ AI-Powered Cloud Cost Optimizer (Web)

        Enter a plain-English description of your cloud project.
        The app will show **each JSON stage** of the pipeline and
        a final **interactive HTML report**:

        1. Project profile JSON (extracted from your description)
        2. Synthetic billing JSON
        3. Full cost-optimization report JSON
        4. Rich HTML dashboard-style report
        """
    )

    with gr.Row():
        description_input = gr.Textbox(
            label="Project Description",
            lines=8,
            placeholder=(
                "Describe your app, tech stack, budget, and requirements.\n"
                "Example: Build an e‑commerce app with React frontend, Node.js backend, "
                "MongoDB, hosted on AWS, budget ₹5000/month, needs scalability and monitoring."
            ),
        )

    run_button = gr.Button("Run Full Analysis 🚀")

    with gr.Row():
        profile_json = gr.JSON(label="1️⃣ Extracted Project Profile (JSON)")
        billing_json = gr.JSON(label="2️⃣ Synthetic Billing Records (JSON)")

    report_json = gr.JSON(label="3️⃣ Cost Optimization Report (JSON)")
    html_report = gr.HTML(label="4️⃣ Interactive HTML Report")

    run_button.click(
        fn=run_pipeline,
        inputs=[description_input],
        outputs=[profile_json, billing_json, report_json, html_report],
    )


if __name__ == "__main__":
    demo.launch()

import json
import os
import re
import time
from datetime import datetime
from pathlib import Path

import streamlit as st
from PIL import Image, ImageEnhance
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()
APP_DIR = Path(__file__).parent
OUTPUT_DIR = APP_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

st.set_page_config(page_title="Prompt Studio | AI Image Generator", page_icon="🎨", layout="wide")

st.markdown("""
<style>
  .stApp {background: linear-gradient(135deg,#f7f8fc 0%,#eef2ff 100%);}
  .block-container {max-width: 1250px; padding-top: 2rem; padding-bottom: 3rem;}
  .hero {padding: 1.6rem 1.8rem; border-radius: 22px; color: white;
         background: linear-gradient(120deg,#111827,#312e81); margin-bottom: 1.2rem;}
  .hero h1 {margin:0; font-size:2.25rem;}
  .hero p {margin:.55rem 0 0; color:#e0e7ff;}
  .panel {background:white; border:1px solid #e5e7eb; padding:1.2rem;
          border-radius:18px; box-shadow:0 8px 24px rgba(15,23,42,.05);}
  div.stButton > button {border-radius:12px; min-height:2.8rem; font-weight:700;}
  @media (max-width: 700px) {.block-container {padding:1rem .7rem;} .hero h1 {font-size:1.7rem;}}
</style>
<div class="hero">
  <h1>🎨 Prompt Studio</h1>
  <p>Turn text prompts into images with a Stable Diffusion model. Create, preview, and save your results.</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Generation settings")
    model = st.text_input("Hugging Face model ID", value=os.getenv("HF_MODEL", "stabilityai/stable-diffusion-xl-base-1.0"))
    width = st.selectbox("Image width", [512, 768, 1024], index=1)
    height = st.selectbox("Image height", [512, 768, 1024], index=1)
    steps = st.slider("Inference steps", 10, 50, 25)
    guidance = st.slider("Guidance scale", 1.0, 15.0, 7.0, 0.5)
    seed = st.number_input("Seed (-1 = random)", min_value=-1, max_value=2_147_483_647, value=-1, step=1)
    st.caption("More steps may improve detail but take longer. High resolution can require more compute.")

left, right = st.columns([1, 1.1], gap="large")
with left:
    st.subheader("1. Describe your image")
    prompt = st.text_area(
        "Prompt",
        placeholder="Example: A tiny wooden cottage beside a lake at sunrise, cinematic lighting, detailed landscape",
        height=150,
        help="Be specific about subject, setting, style, lighting, and composition."
    )
    negative_prompt = st.text_area(
        "Negative prompt (optional)",
        value="blurry, low quality, distorted, watermark, text",
        height=85
    )
    style = st.selectbox("Prompt style helper", ["None", "Photorealistic", "Digital art", "Anime", "Cinematic", "Watercolor"])
    enhance = st.checkbox("Apply light post-processing (contrast and sharpness)", value=True)
    generate = st.button("✨ Generate image", type="primary", use_container_width=True)

    with st.expander("Prompt-writing tips"):
        st.markdown("""
        - **Subject:** What should be in the image?
        - **Setting:** Where and when is it?
        - **Style:** Photo, illustration, watercolor, 3D, etc.
        - **Lighting/composition:** Golden hour, close-up, wide angle, centered.
        - Avoid personal data and prompts for content you do not have permission to create.
        """)

with right:
    st.subheader("2. Generated result")
    result_slot = st.empty()
    status_slot = st.empty()
    if not generate:
        result_slot.info("Your generated image will appear here.")
        st.caption("Generated files and JSON metadata are stored in the project's outputs/ folder.")

def clean_prompt(text):
    return re.sub(r"\s+", " ", text).strip()

def make_safe_name(text):
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", text[:42]).strip("-").lower()
    return slug or "generated-image"

if generate:
    prompt_clean = clean_prompt(prompt)
    if not prompt_clean:
        st.error("Please enter a prompt before generating an image.")
        st.stop()

    style_suffix = {
        "None": "",
        "Photorealistic": ", photorealistic, natural textures, high detail",
        "Digital art": ", polished digital art, detailed illustration",
        "Anime": ", anime art style, clean linework, expressive colors",
        "Cinematic": ", cinematic composition, dramatic lighting, film still",
        "Watercolor": ", watercolor painting, soft pigments, paper texture",
    }[style]
    final_prompt = prompt_clean + style_suffix
    token = os.getenv("HF_TOKEN", "").strip()
    if not token:
        st.error("Hugging Face token not found. Add HF_TOKEN to your .env file, then restart the app. See README.md.")
        st.stop()

    with right:
        with st.spinner("Connecting to the model and generating your image…"):
            try:
                client = InferenceClient(model=model, token=token, timeout=240)
                kwargs = {
                    "prompt": final_prompt,
                    "negative_prompt": clean_prompt(negative_prompt) or None,
                    "num_inference_steps": int(steps),
                    "guidance_scale": float(guidance),
                    "width": int(width),
                    "height": int(height),
                }
                if int(seed) >= 0:
                    kwargs["seed"] = int(seed)
                image = client.text_to_image(**kwargs)
                if not isinstance(image, Image.Image):
                    image = Image.open(image)
                image = image.convert("RGB")
                if enhance:
                    image = ImageEnhance.Contrast(image).enhance(1.04)
                    image = ImageEnhance.Sharpness(image).enhance(1.08)

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                stem = f"{timestamp}_{make_safe_name(prompt_clean)}"
                image_path = OUTPUT_DIR / f"{stem}.png"
                metadata_path = OUTPUT_DIR / f"{stem}.json"
                image.save(image_path, format="PNG", optimize=True)
                metadata = {
                    "created_at": datetime.now().isoformat(timespec="seconds"),
                    "model": model,
                    "prompt": prompt_clean,
                    "final_prompt": final_prompt,
                    "negative_prompt": negative_prompt,
                    "style_helper": style,
                    "parameters": {
                        "steps": int(steps), "guidance_scale": float(guidance),
                        "seed": int(seed) if int(seed) >= 0 else "random",
                        "width": int(width), "height": int(height)
                    },
                    "post_processing": "light contrast/sharpness" if enhance else "none",
                    "image_file": image_path.name
                }
                metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
                result_slot.image(image, caption=f"Generated image · {image.width} × {image.height}", use_container_width=True)
                status_slot.success(f"Saved image and metadata: outputs/{image_path.name}")
                st.download_button("⬇️ Download image", data=image_path.read_bytes(),
                                   file_name=image_path.name, mime="image/png", use_container_width=True)
                with st.expander("View generation metadata"):
                    st.json(metadata)
            except Exception as exc:
                st.error("Image generation failed. Check the model ID, token permissions, internet connection, and Hugging Face model/provider availability.")
                st.code(str(exc))
                st.info("If the model is unavailable through the hosted Inference API, try a model currently supported by your Hugging Face account or run a local Diffusers pipeline.")

st.divider()
st.subheader("Recent saved images")
saved_images = sorted(OUTPUT_DIR.glob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True)
if not saved_images:
    st.caption("No saved images yet. Generate your first image above.")
else:
    cols = st.columns(3)
    for i, path in enumerate(saved_images[:6]):
        with cols[i % 3]:
            st.image(str(path), use_container_width=True)
            st.caption(path.name)
            meta_path = path.with_suffix(".json")
            if meta_path.exists():
                with st.expander("Metadata"):
                    try:
                        st.json(json.loads(meta_path.read_text(encoding="utf-8")))
                    except json.JSONDecodeError:
                        st.warning("Metadata file could not be read.")

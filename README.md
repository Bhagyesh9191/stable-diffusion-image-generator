# Prompt Studio — Stable Diffusion AI Image Generator

A responsive Streamlit web app that generates images from text prompts using the Hugging Face Inference API and a Stable Diffusion-family model. It includes prompt preprocessing, adjustable inference parameters, optional post-processing, image download, and JSON metadata storage.

## Project requirements covered

- Define a text-to-image objective and prompt use cases.
- Use a Stable Diffusion model through an API.
- Configure the Python environment and API token.
- Clean and preprocess prompt text.
- Configure inference steps, guidance scale, dimensions, and seed.
- Generate images from text prompts.
- Apply optional light contrast/sharpness post-processing.
- Save generated images and metadata in `outputs/`.
- Provide a responsive Streamlit interface.
- Test with different prompt styles and record the results.

## Technology

- Python
- Streamlit
- Hugging Face Hub `InferenceClient`
- Pillow
- Stable Diffusion XL model by default

> Hosted model availability, access permissions, and billing/usage limits depend on your Hugging Face account and the selected model/provider. If the default model is not available to your account, select a model currently supported by your Inference API access.

## 1. Prerequisites

Install:
- Python 3.10 or newer
- Git
- A Hugging Face account and access token

Create a token in your Hugging Face settings. Use the minimum permissions needed for inference. **Never commit your real token to GitHub.**

## 2. Download and open the project

Extract the ZIP file, open a terminal in the `stable_diffusion_image_generator` folder, and run the following commands.

### Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `.env` in Notepad and replace `hf_your_token_here` with your actual token.

If PowerShell blocks activation, you can use Command Prompt instead:

```bat
py -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
copy .env.example .env
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

Then edit `.env` and add your real token.

## 3. Run the application

```bash
streamlit run app.py
```

Streamlit will print a local address, normally `http://localhost:8501`. Open it in your browser.

## 4. Generate and test images

1. Enter a descriptive prompt.
2. Optionally enter a negative prompt.
3. Choose a prompt-style helper.
4. Set width/height, inference steps, guidance scale, and seed in the sidebar.
5. Click **Generate image**.
6. Download the result or inspect the metadata.
7. Confirm a PNG and a matching JSON file are created in `outputs/`.

Suggested test prompts:
- **Photorealistic:** `A red bicycle leaning against a brick wall on a rainy street, realistic photography, soft reflections`
- **Digital art:** `A floating island with waterfalls and tiny houses, detailed digital illustration`
- **Cinematic:** `A lone traveler walking through a misty pine forest at dawn, cinematic wide shot`
- **Watercolor:** `A small village beside a river in monsoon, watercolor painting, soft colors`

For the report, record prompt, model, parameters, generation success/failure, output quality, and elapsed time for each test. Model outputs are stochastic, so different seeds/prompts can produce different results.

## 5. Project structure

```text
stable_diffusion_image_generator/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── sample_prompts.csv
└── outputs/
    └── .gitkeep
```

Generated PNGs and JSON metadata go in `outputs/`. That directory is ignored by Git so large generated files are not accidentally pushed. If your assessment requires sample outputs, choose a few small images and deliberately add them to the repository, or upload them separately to Drive.

## 6. Upload to GitHub

1. Sign in to GitHub and create a **new public repository**, for example `stable-diffusion-image-generator`. Do not initialize it with a README if you plan to push this folder's README.
2. Open a terminal in the extracted project folder.
3. Confirm `.env` is ignored and contains your private token. Never paste the token into source code, commits, screenshots, or chat.
4. Run:

```bash
git init
git add .
git status
```

Check the staged file list. `.env`, `.venv`, and generated outputs should not be included.
5. Commit and push (replace the URL with your repository's actual URL):

```bash
git commit -m "Build Stable Diffusion AI image generator"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/stable-diffusion-image-generator.git
git push -u origin main
```

If Git asks you to identify yourself, configure your Git name/email. GitHub typically requires browser authentication or a personal access token for HTTPS Git operations; never use your Hugging Face token for GitHub authentication.

### If you accidentally commit `.env`

Stop pushing, revoke/rotate the exposed Hugging Face token immediately, remove it from the repository history, and verify the repository. Deleting the file in a later commit does not remove the token from previous history.

## 7. Optional: deploy online

You can deploy a Streamlit app using Streamlit Community Cloud or another Python host:
1. Push the project to GitHub.
2. Create a new app and select the repository, branch, and `app.py`.
3. Add `HF_TOKEN` and optionally `HF_MODEL` in the hosting platform's Secrets settings.
4. Deploy and test generation.

Never store the token in public source code. Hosting and model inference may have usage limits or costs.

## Troubleshooting

- **Token missing:** confirm `.env` is in the project root and contains `HF_TOKEN=...`; restart Streamlit.
- **401/403:** check token validity and required permissions.
- **Model/provider unavailable:** choose a model supported by your current Hugging Face Inference API access.
- **Timeout/rate limit:** wait and retry, or lower dimensions and steps.
- **Pillow/Streamlit import error:** activate the virtual environment and run `pip install -r requirements.txt`.
- **Git command not found:** install Git and reopen the terminal.
- **Port already used:** run `streamlit run app.py --server.port 8502`.

## Security and limitations

- The app does not hard-code or transmit your token to the browser; the Python server reads it from `.env`.
- The app saves prompts and generation settings in local JSON metadata. Do not enter confidential or personally identifying information in prompts.
- Hosted inference availability and model output quality depend on the selected model and service status.

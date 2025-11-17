# Ollama Setup Guide (Windows)

Ollama is the simplest way to run local LLMs on Windows. No compilation needed, just download and run.

## Step 1: Download & Install Ollama

1. Go to [https://ollama.ai](https://ollama.ai)
2. Click **Download** → Select **Windows**
3. Run the installer (`OllamaSetup.exe`)
4. Follow the prompts (just click Next/Install)

## Step 2: Start Ollama with Mistral Model

After installation:

1. **Open a new PowerShell terminal** (keep it open)
2. Run:
   ```powershell
   ollama run mistral
   ```
3. Wait for the model to download (~4GB) — first time only
4. You'll see:
   ```
   >>> 
   ```
5. **Keep this terminal open** while running your Flask app

## Step 3: Start Your Flask App

In a **separate PowerShell terminal**:

```powershell
cd c:\Users\karth\reciepe_recommend_local
.\.venv\Scripts\Activate.ps1
python app.py
```

The server will detect Ollama and say:
```
📡 Ollama detected. Using Ollama for local LLM inference.
```

## Step 4: Test It

Once both terminals are running:

1. Open your browser: http://127.0.0.1:5000/cooking-assistant-3d?recipe_id=486640
2. Click "Start Cooking"
3. Try asking a question using the "Ask" button (bottom right)
4. The avatar should answer using the local Mistral LLM!

## Troubleshooting

**Q: "Ollama not running" error**
- Make sure the Ollama terminal is open with `>>> ` prompt visible
- If the model is still downloading, wait until it finishes

**Q: "Ollama run mistral" takes too long**
- First run downloads 4GB model — this is normal
- Subsequent runs are instant

**Q: Slow responses**
- Ollama uses CPU by default (slower but works everywhere)
- If you want GPU: after installing Ollama, CUDA support is automatic on NVIDIA GPUs
- Mistral 7B takes ~5-10 seconds per response on CPU (normal)

**Q: Want a smaller/faster model?**
- Instead of `ollama run mistral`, try:
  - `ollama run neural-chat` (smaller, faster)
  - `ollama run phi` (tiny, very fast)
- Then in Flask, update the model name in `/local-llm` endpoint

## Next: GPU Acceleration (Optional)

If you want faster responses on your RTX 3060:

1. Install CUDA 12.x from NVIDIA
2. Restart Ollama
3. Ollama will auto-detect your GPU

Mistral 7B Q4 is ~60% faster with GPU (still takes 3-5 seconds, but smooth).

---

**Ready?** Open two terminals and follow steps 2 & 3 above!

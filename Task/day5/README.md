# Day 5 Assessment — Three Scenarios
1. Cybersecurity incident explainer (`cyber-explainer`)
2. Photography mentor (`photo-mentor`)
3. Placement aptitude tutor (`aptitude-tutor`)

Requires Ollama, Python, and requests (`pip install requests`).

From this folder:
```powershell
ollama pull qwen2.5:1.5b
ollama create cyber-explainer -f Modelfile.cyber
ollama create photo-mentor -f Modelfile.photo
ollama create aptitude-tutor -f Modelfile.aptitude
ollama list
python api_demo.py
```
Capture actual screenshots in `screenshots/`: `ollama list`, `ollama show` for each custom model, `ollama ps` while loaded, and script output. Fill actual observations and timings in `analysis.md`; do not invent measurements.

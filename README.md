# stegPE — Steganographic Prompt Injection Research Lab

> A controlled sandbox for measuring steganographic prompt injection susceptibility in local LLM agents and evaluating pre-inference sanitization defenses.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Platform](https://img.shields.io/badge/Platform-Ubuntu%2024.04-orange)
![LLM](https://img.shields.io/badge/LLM-Llama%203%20%28Ollama%29-green)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## What This Project Does

This lab embeds malicious text prompts inside ordinary looking images using steganography, feeds those images to a local LLM agent, and measures:

- Whether the hidden payload influences the agent's responses
- Whether pre-inference scanners can detect the payload
- Whether image sanitization removes the payload before it reaches the model

**Key finding:** LSB steganography survives PIL sanitization. EXIF payloads do not. This asymmetric defense gap has direct implications for production AI pipelines.

---

## Project Structure

```
stegPE/
├── images/                    # generated images 
│   └── README.txt
├── scripts/
│   ├── image.py               # Generate realistic carrier image
│   ├── encoder.py             # Embed payloads via LSB and EXIF
│   ├── decoder.py             # Extract and verify payloads
│   ├── scanner.py             # Detection robustness tests
│   └── agent.py               # LLM agent with defense layer
├── notebooks/
│   └── analysis.ipynb         # Full analysis and charts
├── logs/                      # Generated during runs
│   ├── agent_log.jsonl
│   ├── results_summary.json
│   └── scanner_report.json
└── requirements.txt
```

---

## Setup

### Prerequisites

- VirtualBox with Ubuntu 24.04 guest (Host-Only network adapter)
- Python 3.10+
- [Ollama](https://ollama.com) installed

### Installation

```bash
# Clone the repository
git clone https://github.com/[your-username]/stegPE.git
cd stegPE

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Register Jupyter kernel
python -m ipykernel install --user --name=stegPE --display-name "Python (stegPE)"

# Pull local LLM (runs fully offline)
ollama pull llama3
```

---

## Run Order

```bash
source venv/bin/activate

# Step 1 — Create a realistic carrier image
python scripts/image.py

# Step 2 — Embed payloads using LSB and EXIF
python scripts/encoder.py

# Step 3 — Verify payloads were embedded
python scripts/decoder.py

# Step 4 — Run detection robustness tests
python scripts/scanner.py

# Step 5 — Run LLM agent experiments
python scripts/agent.py

# Step 6 — Open analysis notebook
jupyter notebook notebooks/analysis.ipynb
```

---

## Results

```
Total images scanned   : 6
LSB payloads detected  : 3/6
EXIF payloads detected : 2/6

After PIL sanitization:
LSB payloads survive   : 3/6  - Gap
EXIF payloads survive  : 0/6  - Defense
```

---

## Security Notice

> This project is for **defensive security research only**.
> All experiments must be run in an **air-gapped virtual machine**.

---

## Extending This Research

| Direction | How |
|---|---|
| Test more models | `ollama pull mistral` or `ollama pull phi3` — edit model name in agent.py |
| Vision model testing | `ollama pull llava` — test if model visually detects stego patterns |
| Semantic drift measurement | Add `sentence-transformers` cosine similarity between control and injected responses |
| DCT steganography | Replace LSB encoder with a JPEG DCT-domain method |
| Pixel noise defense | Add random LSB noise injection step before inference |

---
## Read the Blog
Medium write-up: 

---
## License

MIT License — see LICENSE file for details.

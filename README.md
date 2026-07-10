# Basic-Pitch-GUI 🎶➡️🎹
Audio to MIDI converter powered by Basic Pitch, perfect for VOCALOID and etc.

Run locally, convert audio to MIDI with ease!  
Powered by [Basic Pitch](https://github.com/spotify/basic-pitch), this project offers a friendly GUI + CLI for pitch detection and conversion — no internet required.

---

## ✨ Features
- 🖥️ **GUI + CLI** modes for all users
- 🎵 **Audio → MIDI conversion** (supports vocals & instruments in **.mp3 & .ogg & .wav & .flac & .m4a** format)
- ⚙️ **Adjustable advanced parameters**:
  - Onset threshold  
  - Frame threshold  
  - Minimum note length  
  - Frequency range
- 🌐 **Bilingual UI**: English / 中文
- 💾 **Persistent settings** saved in `settings.ini`
- 📦 **Standalone exe** for Windows

---

## 🎯 Use Cases
- 🎤 Vocaloid production workflows  
- 🎼 Music composition & arrangement  
- 🎹 Music production and DAW integration  
- 📚 Learning transcription & pitch analysis  

---

## 🚀 Getting Started

<details>
<summary>🛠️ Manual Installation</summary>

1. Clone the repo:
   ```
   git clone https://github.com/charles23333333/basic-pitch-gui.git
   cd basic-pitch-gui
   ···
👉 uv is recommended for installation and running.

👉 Python ≤ 3.13.0 is required, and the pre‑build exe is packaged with Python 3.10.
2. Install dependencies
```
uv pip install -r requirements.txt
```
3.Run!

Run GUI:
```
uv run gui.py
```
Run CLI:
```
uv run cli.py input.wav -o output_dir
```
</details>

<details>
<summary>📦 Prebuilt Executable</summary>

👉 You can also use the prebuilt exe for one‑click run, available from the Release section.

Just download the latest .exe from Releases.

Double‑click to run — no Python environment required.
</details>

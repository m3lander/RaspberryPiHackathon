# Repository Guidelines

## Project Structure & Module Organization
- `main.py` runs the assistant; supporting scripts live in the repo root (e.g., `train_wakeword.py`, `test_full_flow.py`).
- `camera/` contains camera backends (`usb_camera.py`, `pi_camera.py`, `base.py`).
- `tools/` contains Gemini-powered analyzers (`item_recognition.py`, `cash_recognition.py`, `packaging_reader.py`).
- `hotword_training_audio/` stores wake-word samples; `hotword_refs/` stores trained models.
- Configuration is template-driven via `env.template` → `.env` (never commit `.env`).

## Build, Test, and Development Commands
- `./setup_pi.sh`: installs system deps and creates `.venv` on a Raspberry Pi.
- `source .venv/bin/activate`: activates the Python 3.11 venv created by setup.
- `cp env.template .env` and edit `.env`: set API keys and camera/wake-word settings.
- `python train_wakeword.py`: trains the wake-word model into `hotword_refs/`.
- `python test_camera_capture.py`: verifies camera capture only.
- `python test_camera_gemini.py`: verifies camera + Gemini analysis.
- `python test_full_flow.py`: end-to-end test (camera → Gemini → ElevenLabs TTS).
- `python main.py`: runs the voice assistant.

## Coding Style & Naming Conventions
- Python, 4-space indentation, module-level docstrings are common.
- `snake_case` for functions/variables, `PascalCase` for classes, `ALL_CAPS` for env vars.
- Keep type hints where present and prefer small, focused functions.
- No formatter/linter is configured; keep changes consistent with existing style.

## Testing Guidelines
- Tests are script-style (`test_*.py`) and run manually from the repo root.
- Name new tests `test_<feature>.py` and keep outputs (e.g., saved images) out of git.

## Commit & Pull Request Guidelines
- Recent commits use short, sentence-case subjects without prefixes; follow that pattern.
- PRs should describe hardware context (Pi model, camera type), list test scripts run, and note any `.env` changes without exposing secrets.

## Agent & Configuration Notes
- ElevenLabs agent setup lives in `SETUP_AGENT.md` and is required for `main.py`.
- Keep API keys and agent IDs in `.env`; update `env.template` only for new required vars.

# AUREX Workstation — preview v1

Lightweight local dashboard; no Docker or pip packages required.

## Chromebook

From a checkout of this repository:

```bash
python3 workstation/app.py
```

Open **http://127.0.0.1:8765** in Chrome.

To target the **separate** Chromebook offline AUREX v3 installation:

```bash
AUREX_LOCAL_ROOT="$HOME/aurex-offline-v3" python3 workstation/app.py
```

Buttons run only the existing `run_tests.sh` and `verify_gate.py` in that specified local project. The commands have 90-second timeouts and capture output. **Do not expose the service to the internet.** Use only a trusted local project directory.

## What is and is not verified

- Exit status 0 is shown as PASS for the invoked command only.
- A successful `verify_gate.py` command **does not imply** the evidence gate reached VERIFIED; read its output.
- HLE-style practice, model integrations, independent evidence authentication, and production security efficacy are **not implemented** in this preview.
- This repository and the separate local Chromebook folder are not automatically synchronized.
- No merge, deployment, Docker installation, or official HLE run is performed by adding this code.

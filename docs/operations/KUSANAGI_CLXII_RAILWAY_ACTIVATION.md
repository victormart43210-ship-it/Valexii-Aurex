# OPERATION KUSANAGI CLXII — RAILWAY ACTIVATION REPORT

## Docker Packaging Verification
- **Root Dockerfile**: Confirmed  and Obtaining file:///app
  Installing build dependencies: started
  Installing build dependencies: finished with status 'done'
  Checking if build backend supports build_editable: started
  Checking if build backend supports build_editable: finished with status 'done'
  Getting requirements to build editable: started
  Getting requirements to build editable: finished with status 'done'
  Preparing editable metadata (pyproject.toml): started
  Preparing editable metadata (pyproject.toml): finished with status 'done'
Requirement already satisfied: pydantic<3,>=2.9 in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from valexii-aurex==0.1.0a1) (2.14.1)
Requirement already satisfied: fastapi<1,>=0.115 in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from valexii-aurex==0.1.0a1) (0.150.0)
Requirement already satisfied: uvicorn<1,>=0.32 in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from valexii-aurex==0.1.0a1) (0.54.0)
Requirement already satisfied: cryptography<47,>=46.0.5 in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from valexii-aurex==0.1.0a1) (46.0.7)
Requirement already satisfied: pytest<9,>=8 in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from valexii-aurex==0.1.0a1) (8.4.2)
Requirement already satisfied: ruff<1,>=0.8 in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from valexii-aurex==0.1.0a1) (0.17.1)
Requirement already satisfied: mypy<2,>=1.13 in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from valexii-aurex==0.1.0a1) (1.20.2)
Requirement already satisfied: httpx<1,>=0.27 in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from valexii-aurex==0.1.0a1) (0.28.1)
Requirement already satisfied: cffi>=2.0.0 in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from cryptography<47,>=46.0.5->valexii-aurex==0.1.0a1) (2.1.1)
Requirement already satisfied: starlette>=0.46.0 in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from fastapi<1,>=0.115->valexii-aurex==0.1.0a1) (1.9.0)
Requirement already satisfied: typing-extensions>=4.8.0 in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from fastapi<1,>=0.115->valexii-aurex==0.1.0a1) (4.16.0)
Requirement already satisfied: typing-inspection>=0.4.2 in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from fastapi<1,>=0.115->valexii-aurex==0.1.0a1) (0.4.4)
Requirement already satisfied: annotated-doc>=0.0.2 in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from fastapi<1,>=0.115->valexii-aurex==0.1.0a1) (0.0.5)
Requirement already satisfied: opentelemetry-api>=1.44.0 in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from fastapi<1,>=0.115->valexii-aurex==0.1.0a1) (1.45.1)
Requirement already satisfied: anyio in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from httpx<1,>=0.27->valexii-aurex==0.1.0a1) (4.15.1)
Requirement already satisfied: certifi in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from httpx<1,>=0.27->valexii-aurex==0.1.0a1) (2026.10.18)
Requirement already satisfied: httpcore==1.* in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from httpx<1,>=0.27->valexii-aurex==0.1.0a1) (1.0.9)
Requirement already satisfied: idna in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from httpx<1,>=0.27->valexii-aurex==0.1.0a1) (3.20)
Requirement already satisfied: h11>=0.16 in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from httpcore==1.*->httpx<1,>=0.27->valexii-aurex==0.1.0a1) (0.16.0)
Requirement already satisfied: mypy_extensions>=1.0.0 in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from mypy<2,>=1.13->valexii-aurex==0.1.0a1) (1.1.0)
Requirement already satisfied: pathspec>=1.0.0 in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from mypy<2,>=1.13->valexii-aurex==0.1.0a1) (1.1.1)
Requirement already satisfied: librt>=0.8.0 in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from mypy<2,>=1.13->valexii-aurex==0.1.0a1) (0.16.0)
Requirement already satisfied: annotated-types>=0.6.0 in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from pydantic<3,>=2.9->valexii-aurex==0.1.0a1) (0.8.0)
Requirement already satisfied: pydantic-core==2.50.1 in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from pydantic<3,>=2.9->valexii-aurex==0.1.0a1) (2.50.1)
Requirement already satisfied: iniconfig>=1 in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from pytest<9,>=8->valexii-aurex==0.1.0a1) (2.3.1)
Requirement already satisfied: packaging>=20 in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from pytest<9,>=8->valexii-aurex==0.1.0a1) (26.3)
Requirement already satisfied: pluggy<2,>=1.5 in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from pytest<9,>=8->valexii-aurex==0.1.0a1) (1.7.0)
Requirement already satisfied: pygments>=2.7.2 in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from pytest<9,>=8->valexii-aurex==0.1.0a1) (2.21.0)
Requirement already satisfied: click>=7.0 in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from uvicorn<1,>=0.32->valexii-aurex==0.1.0a1) (8.5.0)
Requirement already satisfied: pycparser in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from cffi>=2.0.0->cryptography<47,>=46.0.5->valexii-aurex==0.1.0a1) (3.11)
Building wheels for collected packages: valexii-aurex
  Building editable for valexii-aurex (pyproject.toml): started
  Building editable for valexii-aurex (pyproject.toml): finished with status 'done'
  Created wheel for valexii-aurex: filename=valexii_aurex-0.1.0a1-0.editable-py3-none-any.whl size=7545 sha256=940fbf6e391cde4a1f7663b2507128cd4acf76fb3686435ce76e729ade0b5074
  Stored in directory: /tmp/pip-ephem-wheel-cache-snwoai8t/wheels/54/1b/b7/aa63e25c8f14f4f2ae7b04e6097bdecb770e455c5c1ee0a600
Successfully built valexii-aurex
Installing collected packages: valexii-aurex
  Attempting uninstall: valexii-aurex
    Found existing installation: valexii-aurex 0.1.0a1
    Uninstalling valexii-aurex-0.1.0a1:
      Successfully uninstalled valexii-aurex-0.1.0a1
Successfully installed valexii-aurex-0.1.0a1 present.
- **Staging Dockerfile**:  copies , , and  before running Processing ./.
  Installing build dependencies: started
  Installing build dependencies: finished with status 'done'
  Getting requirements to build wheel: started
  Getting requirements to build wheel: finished with status 'done'
  Preparing metadata (pyproject.toml): started
  Preparing metadata (pyproject.toml): finished with status 'done'
Requirement already satisfied: pydantic<3,>=2.9 in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from valexii-aurex==0.1.0a1) (2.14.1)
Requirement already satisfied: fastapi<1,>=0.115 in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from valexii-aurex==0.1.0a1) (0.150.0)
Requirement already satisfied: uvicorn<1,>=0.32 in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from valexii-aurex==0.1.0a1) (0.54.0)
Requirement already satisfied: cryptography<47,>=46.0.5 in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from valexii-aurex==0.1.0a1) (46.0.7)
Requirement already satisfied: cffi>=2.0.0 in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from cryptography<47,>=46.0.5->valexii-aurex==0.1.0a1) (2.1.1)
Requirement already satisfied: starlette>=0.46.0 in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from fastapi<1,>=0.115->valexii-aurex==0.1.0a1) (1.9.0)
Requirement already satisfied: typing-extensions>=4.8.0 in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from fastapi<1,>=0.115->valexii-aurex==0.1.0a1) (4.16.0)
Requirement already satisfied: typing-inspection>=0.4.2 in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from fastapi<1,>=0.115->valexii-aurex==0.1.0a1) (0.4.4)
Requirement already satisfied: annotated-doc>=0.0.2 in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from fastapi<1,>=0.115->valexii-aurex==0.1.0a1) (0.0.5)
Requirement already satisfied: opentelemetry-api>=1.44.0 in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from fastapi<1,>=0.115->valexii-aurex==0.1.0a1) (1.45.1)
Requirement already satisfied: annotated-types>=0.6.0 in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from pydantic<3,>=2.9->valexii-aurex==0.1.0a1) (0.8.0)
Requirement already satisfied: pydantic-core==2.50.1 in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from pydantic<3,>=2.9->valexii-aurex==0.1.0a1) (2.50.1)
Requirement already satisfied: click>=7.0 in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from uvicorn<1,>=0.32->valexii-aurex==0.1.0a1) (8.5.0)
Requirement already satisfied: h11>=0.8 in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from uvicorn<1,>=0.32->valexii-aurex==0.1.0a1) (0.16.0)
Requirement already satisfied: pycparser in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from cffi>=2.0.0->cryptography<47,>=46.0.5->valexii-aurex==0.1.0a1) (3.11)
Requirement already satisfied: anyio<5,>=4.0.0 in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from starlette>=0.46.0->fastapi<1,>=0.115->valexii-aurex==0.1.0a1) (4.15.1)
Requirement already satisfied: idna>=2.8 in /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages (from anyio<5,>=4.0.0->starlette>=0.46.0->fastapi<1,>=0.115->valexii-aurex==0.1.0a1) (3.20)
Building wheels for collected packages: valexii-aurex
  Building wheel for valexii-aurex (pyproject.toml): started
  Building wheel for valexii-aurex (pyproject.toml): finished with status 'done'
  Created wheel for valexii-aurex: filename=valexii_aurex-0.1.0a1-py3-none-any.whl size=171555 sha256=16c899a9b70b8c2343085c9795857f692958ea2147248d480a193b0ef0a5734e
  Stored in directory: /tmp/pip-ephem-wheel-cache-d4hfaz90/wheels/54/1b/b7/aa63e25c8f14f4f2ae7b04e6097bdecb770e455c5c1ee0a600
Successfully built valexii-aurex
Installing collected packages: valexii-aurex
  Attempting uninstall: valexii-aurex
    Found existing installation: valexii-aurex 0.1.0a1
    Uninstalling valexii-aurex-0.1.0a1:
      Successfully uninstalled valexii-aurex-0.1.0a1
Successfully installed valexii-aurex-0.1.0a1.
- **Startup Entrypoint**:  imports  directly.

## Route Registration & Verification Matrix
| Endpoint | Method | Purpose | Status |
|---|---|---|---|
|  | GET | Health & Capability Check | PASS |
|  | GET | Operational Feature Capabilities | PASS |
|  | GET | Evidence Record Retrieval | PASS |
|  | GET | System Budget Governance | PASS |
|  | GET / POST | Job State Management | PASS |
|  | GET | Job Audit Receipt | PASS |
|  | GET | XAELI Operational Readiness Findings | PASS |
|  | POST | Towing & Oilfield Synthetic Demo Audit | PASS |

## Test Baseline
- **Pytest**: 455 passed, 1 skipped.
- **Ruff**: Clean (0 errors).
- **Mypy**: Clean (0 errors in 79 source files).

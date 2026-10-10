"""Local-only, dependency-free AUREX workstation preview.

Run: python3 workstation/app.py
Open: http://127.0.0.1:8765
This UI never asserts product authority or benchmark certification.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
import html
import json
import os
import subprocess
import sys
from model_client import generate
from local_diagnostics import diagnose

ROOT = Path(__file__).resolve().parents[1]
LOCAL = Path(os.environ.get("AUREX_LOCAL_ROOT", str(ROOT))).expanduser().resolve()
HOST = "127.0.0.1"
PORT = int(os.environ.get("AUREX_PORT", "8765"))
MAX_OUTPUT = 16000

def run_check(name):
    if name == "tests":
        script = LOCAL / "run_tests.sh"
        if not script.is_file():
            return {"status": "NOT_RUN", "output": "No run_tests.sh found in selected local project."}
        command = ["bash", str(script)]
    elif name == "hle":
        folder = ROOT / "workstation" / "hle_practice_data"
        script = ROOT / "workstation" / "hle_practice.py"
        dataset = folder / "questions.json"
        responses = folder / "responses.example.json"
        if not all(p.is_file() for p in (script, dataset, responses)):
            return {"status": "NOT_RUN", "output": "Practice files missing."}
        command = [sys.executable, str(script), "--dataset", str(dataset), "--responses", str(responses)]
    elif name == "gate":
        script = LOCAL / "verify_gate.py"
        if not script.is_file():
            return {"status": "NOT_RUN", "output": "No verify_gate.py found in selected local project."}
        command = [sys.executable, str(script)]
    else:
        return {"status": "NOT_RUN", "output": "Unknown check."}
    try:
        completed = subprocess.run(command, cwd=LOCAL, capture_output=True,
                                   text=True, timeout=90, stdin=subprocess.DEVNULL,
                                   env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        output = (completed.stdout + "\n" + completed.stderr)[-MAX_OUTPUT:]
        return {"status": "PASS" if completed.returncode == 0 else "FAIL",
                "exit_code": completed.returncode, "output": output}
    except subprocess.TimeoutExpired:
        return {"status": "TIMEOUT", "output": "Check exceeded 90 seconds."}
    except OSError as exc:
        return {"status": "ERROR", "output": str(exc)}

PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AUREX Workstation</title>
<style>
:root{color-scheme:dark;font-family:system-ui,sans-serif;background:#07131b;color:#e8f5f7}
body{max-width:1050px;margin:auto;padding:28px}
header{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap}
h1{letter-spacing:.15em;font-size:2rem;color:#66e7dc}h2{font-size:1.2rem}
small,.muted{color:#a2b7bf}.badge{border:1px solid #b78b40;padding:8px 12px;border-radius:20px;color:#ffce7a}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px;margin-top:24px}
.card{background:#11242f;border:1px solid #28505a;border-radius:16px;padding:20px}
button{background:#0eb6ae;color:#05171b;border:0;border-radius:10px;padding:13px 18px;font-weight:750;cursor:pointer}
button:disabled{opacity:.55;cursor:wait}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#061017;padding:15px;border-radius:10px;min-height:60px}
a{color:#79e6e0}.foot{margin-top:30px;font-size:.9rem}
</style></head><body><header><div><small>VALEXII.AI / LOCAL WORKSTATION</small>
<h1>AUREX</h1><p>Evidence • Qualification • Reality • Authority • Effect</p></div>
<span class="badge">NO AUTOMATIC VERIFICATION</span></header>
<p class="muted">Local dashboard. Passing a test means that specific test command exited successfully;
it does not certify HLE performance or grant BCXMET authority.</p>
<div class="grid">
<section class="card"><h2>Security regression</h2><p>Run the local AUREX test script.</p>
<button onclick="check('tests',this)">Run security tests</button><pre id="tests">NOT RUN in this session</pre></section>
<section class="card"><h2>Evidence gate</h2><p>Inspect the existing adversarial gate. Fail-closed is preserved.</p>
<button onclick="check('gate',this)">Check evidence gate</button><pre id="gate">NOT RUN in this session</pre></section>
<section class="card"><h2>HLE-style practice</h2><p>Score three prepared answers. No AI model or official HLE data.</p>
<button onclick="check('hle',this)">Run HLE practice</button><pre id="hle">NOT RUN in this session</pre></section>
<section class="card"><h2>Local model readiness</h2><p>Check whether llama.cpp and model files are available without running inference.</p>
<button onclick="check('local',this)">Check local AI</button><pre id="local">NOT RUN in this session</pre></section>
<section class="card"><h2>Ask a model</h2><p>Optional OpenAI-compatible endpoint; no model configured by default.</p>
<textarea id="question" rows="4" maxlength="4000" style="width:100%;box-sizing:border-box;background:#061017;color:#e8f5f7" placeholder="Enter a practice question"></textarea>
<button onclick="askModel(this)">Generate answer</button><pre id="model-result">NOT CONFIGURED</pre></section>
</div><p class="foot">Bound to localhost only. No remote execution, public uploads, or changes to product authority.</p>
<script>
async function check(name,button){
 const output=document.getElementById(name);button.disabled=true;output.textContent='Running…';
 try{
 const response=await fetch('/api/check/'+name,{method:'POST'});
 const result=await response.json();
 output.textContent=result.status+'\\n'+(result.output||'');
 }catch(err){output.textContent='ERROR: '+err.message}
 finally{button.disabled=false}
}
async function askModel(button){
 const output=document.getElementById('model-result');
 button.disabled=true;output.textContent='Generating…';
 try{
 const response=await fetch('/api/model/generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:document.getElementById('question').value})});
 const result=await response.json();
 output.textContent=result.status+'\\n'+(result.answer||result.output||'')+'\\nIndependent validation: NOT_VERIFIED';
 }catch(err){output.textContent='ERROR: '+err.message}
 finally{button.disabled=false}
}
</script></body></html>"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if urlsplit(self.path).path != "/":
            self.send_error(404)
            return
        data = PAGE.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        path = urlsplit(self.path).path
        if path not in ("/api/check/tests", "/api/check/gate", "/api/check/hle", "/api/check/local", "/api/model/generate"):
            self.send_error(404)
            return
        # Browser-origin check reduces cross-site requests to the local service.
        origin = self.headers.get("Origin")
        if origin and origin not in (f"http://{HOST}:{PORT}", f"http://localhost:{PORT}"):
            self.send_error(403)
            return
        if path == "/api/model/generate":
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length < 1 or length > 8192:
                    raise ValueError("Invalid request size")
                payload = json.loads(self.rfile.read(length))
                if not isinstance(payload, dict):
                    raise ValueError("Expected JSON object")
                result = generate(payload.get("question"))
            except Exception as exc:
                result = {"status": "ERROR", "output": str(exc), "independent_validation": "NOT_VERIFIED"}
        elif path == "/api/check/local":
            result = {"status": "DIAGNOSTIC_ONLY", "output": json.dumps(diagnose(), indent=2)}
        else:
            result = run_check(path.rsplit("/", 1)[-1])
        data = json.dumps(result).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

if __name__ == "__main__":
    print(f"AUREX workstation: http://{HOST}:{PORT}")
    print(f"Local project: {LOCAL}")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()

# Runtime verification (native Qwen and local adapters)

Steps to verify the native model runtime on the target machine (AUREX-OX):

1. Verify local model server is running (loopback only)
   - Expected endpoint (example): http://127.0.0.1:8080/v1
   - Confirm with: curl -sS --max-time 2 http://127.0.0.1:8080/v1/health
2. Verify authenticated inference gateway (if present): http://127.0.0.1:8944
3. Use a harmless synthetic prompt and check the full request/response shape
4. Confirm timeouts and max response size are respected by the adapter
5. Confirm adapter enforces `local_loopback=True` and rejects external hostnames
6. Confirm no external (paid) provider is called when budget = $0.00

What to capture

- Gateway version string from the local service
- Model identifier
- Latency measurements
- Sample request and response JSON (redact any sensitive fields)

Failure modes

- Model process not started -> adapter should report explicit failure
- Model returns malformed JSON -> adapter should raise and persist a HOLD witness
- Response too large -> abort and persist an INSUFFICIENT/CONTESTED witness


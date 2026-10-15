#!/usr/bin/env python3
"""Explicit local model smoke test; never invoked by installer."""
import argparse

from aurex.local_inference import run_local_inference

p = argparse.ArgumentParser(description='Explicitly approved local AUREX inference smoke test')
p.add_argument('--backend', choices=['llama.cpp','ollama'], default='llama.cpp')
p.add_argument('--base-url', default='http://127.0.0.1:8080')
p.add_argument('--model', required=True)
p.add_argument('--prompt', default='Reply with the word READY.')
p.add_argument('--approve-local-inference', action='store_true', required=True)
a = p.parse_args()
r = run_local_inference(prompt=a.prompt, model=a.model, base_url=a.base_url,
                        backend=a.backend, approved=a.approve_local_inference)
print('PROVIDER:', r.provider)
print('MODEL:', r.model)
print('UNVERIFIED OUTPUT:', r.text)
print('SHA256:', r.sha256)
print('AUTHORITY GRANTED:', r.authority_granted)

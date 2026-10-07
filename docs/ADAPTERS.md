# Model adapters

AUREX keeps model providers outside the evidence/authority protocol.

## OpenAI-compatible endpoints

Use `OpenAICompatibleAdapter` for servers exposing a compatible `/chat/completions` endpoint. Credentials are read only from an environment variable chosen by the caller. Do not commit keys.

## Ollama

`OllamaAdapter` targets a local Ollama endpoint and defaults to loopback. A local model can therefore act as an additional witness without requiring its output to become product authority.

## Independence

For critical evaluations, claimant and verifier should not silently collapse into the same model/provider/configuration. Provider/model identity belongs in evaluation evidence.

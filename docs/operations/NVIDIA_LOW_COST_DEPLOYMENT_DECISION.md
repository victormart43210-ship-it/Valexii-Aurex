# NVIDIA low-cost decision — 2026-10-26

Decision: keep the synthetic audit deterministic and use existing loopback inference only when an appropriately sized model is already available. Incremental external inference cost for this operation: $0. No GPU purchase or paid request. The workload has not been measured, so a globally cheapest live provider cannot honestly be selected yet.

## Options

| Class | Decision and constraints |
|---|---|
| Existing CPU/local Ollama or llama.cpp | First choice for optional synthetic explanations if memory and latency are adequate; electricity and existing hosting remain real costs. No GPU assumption. |
| NVIDIA developer API | Evaluation candidate only after separate authorization and account-specific terms/limits verification. Not a production entitlement. |
| Hosted production API | Potentially economical for sparse usage; select model, token price and contractual cap before comparison. No verified account quote available. |
| Scale-to-zero GPU | Candidate after demand measurement; startup, execution, idle retention and storage all count. |
| On-demand GPU | Bounded experiment only after approval; storage can continue billing when stopped. |
| Dedicated GPU | Not justified by current unmeasured synthetic workload; no provisioning. |

NVIDIA's official FAQ distinguishes developer prototyping from production; its published AI Enterprise starting license is $4,500/GPU/year or approximately $1/GPU/hour in cloud. Hardware/cloud usage is additional. Verify the selected model license separately; NVIDIA acceleration does not confer model rights. Self-hosted NIM requires supported CUDA hardware. No NIM fit has been verified on Hetzner.
Source: https://docs.api.nvidia.com/nim/docs/product (checked 2026-10-26).

## Illustrative arithmetic, not a quote or measured performance

Runpod lists RTX 3090 24GB at $0.50/hour and standard network storage below 1TB at $0.07/GB/month. For 20GB persistent storage, assumed $1.40/month: one compute hour totals $1.90; ten hours $6.40; continuous 730 hours $366.40. These exclude container storage, tax and any separate software license. If container disk is 20GB and retained for the whole month at $0.10/GB/month, add $2.00. Runpod billing docs state no data-transfer fee. Account deposit requirements and availability must be verified before approval. Serverless storage docs specify five-minute container-disk intervals; do not treat worker compute time alone as the total.
Sources: https://www.runpod.io/pricing ; https://docs.runpod.io/accounts-billing/billing ; https://docs.runpod.io/serverless/pricing (checked 2026-10-26).

A hosted token estimate must be calculated as input_tokens/1,000,000 * input_price + output_tokens/1,000,000 * output_price, plus minimums/storage/transfer. No selected NVIDIA-compatible production model or account price is verified; no invented monthly total is provided for that path.

## Admission and migration

Record actual Hetzner RAM/CPU/disk and model peak memory before choosing quantization or context. A small CPU server is not assumed capable of large Qwen. Keep the runner for verification. First benchmark a synthetic small local model; then compare measured throughput and usage with a hosted quote. NIM GPU compatibility must be checked for the exact model/runtime, not inferred from VRAM alone.

Remote execution currently hard-denies. Before implementing an enable path require durable transactional reservations, idempotent request IDs, concurrency/restart tests, stale/revoked authorization rejection, endpoint/model allowlists, bounded tokens/deadline, no automatic retry/refund on ambiguous failures, redacted decision records, and provider-side controls. Account spending caps, key restrictions, model limits, alerts and actual rate limits are NOT VERIFIED for the owner's NVIDIA account. Do not infer caps from forum anecdotes or API-key existence. A client reservation cannot guarantee a provider billing cap.

Owner approval is required for any paid account configuration, GPU allocation or external inference. No account or credential changes were made. Production HOLD.

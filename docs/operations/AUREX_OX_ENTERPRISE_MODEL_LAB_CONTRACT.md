# AUREX-OX — Enterprise Model Laboratory Contract (CCXLIII addendum)

Status: PROPOSED CONTRACT / NO IMPLEMENTATION. Production HOLD. Financial authority NONE. No external paid inference, uncontrolled training, customer uploads or automatic deployments.

## Product intent
AUREX-OX (also referenced by owner as RX/OX) is a sovereign AI experimentation, model evaluation, optimization, and enterprise customization platform. It is both the governed intelligence backbone for DISPATER.AI, XAELI and BCXMET, **and** a potential commercial service for companies requiring task- and industry-specific AI. The company sells validated outcomes and isolated model solutions, not merely access to a general-purpose chatbot.

## Core workspaces
1. **Model catalog:** upstream origin, license/weights/dataset restrictions, pinned revision, model card, dependency SBOM, permitted usage, deployment constraints.
2. **Evaluation laboratory:** frozen synthetic/authorized test datasets, task-specific metrics, reproducible inference, adversarial red-team, independent baseline/oracle, comparison across Qwen/K2/Falcon and approved candidates.
3. **Customization laboratory:** progressive options from prompt/tool/RAG configurations through quantization, PEFT/LoRA and fine-tuning; full training only after cost, data rights, hardware and safety approval. Track training code, hyperparameters, dataset lineage and model artifact digests.
4. **Enterprise tenant workspaces:** isolated keys, data, retrieval indexes, adapters, fine-tuned weights, evaluation results, usage and retention; prohibit cross-tenant training or reuse without explicit contract/consent.
5. **Model registry and release gates:** candidate -> benchmarked -> independently verified -> approved -> deployed -> monitored -> retired; rollback to pinned previous versions. No model may promote itself.
6. **Customer delivery:** private API/on-prem deployment, RAG service, task-specific agent or model package as authorized; explicit SLA, scope, compliance, cost and maintenance boundaries.

## Minimum contracts
- `ModelCandidate`: model_id, upstream_url, immutable_revision, weight_digest, tokenizer_digest, code_digest, license_record, architecture, hardware_limits, trust_remote_code_review.
- `EvaluationRun`: tenant_id, task_id, dataset_digest, independent_oracle_digest, candidate_digest, baseline_digest, prompt_digest, environment_digest, per-case result digests, metrics, costs, replay_manifest_digest.
- `CustomizationJob`: tenant_id, base_model_digest, customization_method, authorized_dataset_ids, data_rights_receipt, training_config_digest, isolated_artifact_digest, evaluation_run_id, human_approval_state.
- `DeploymentApproval`: tenant_id, target_environment, model_digest, approved_use_cases, prohibited_actions, risk_level, reviewer_identity, rollback_ref, expiry.
- `ModelProvenanceDAG`: base weights -> customization artifacts -> benchmark evidence -> independent approval -> runtime deployment; no unverified edge may grant financial/security authority.

## Technical rules
- Default all model experiments and integrations OFF. No silent downloads, API charges or remote model calls.
- Keep money math, audit findings, and authority qualification deterministic outside LLMs. A model may propose, extract or explain; it may not approve a recovery amount, security action or its own evaluation.
- Prefer cheapest sufficient customization path; benchmark RAG/prompt/tools against LoRA before training.
- Dataset rights and license clearance must cover both training and commercial customer delivery; separate code, model-weight and dataset licenses.
- Training/evaluation data must be partitioned by customer, with no benchmark contamination; report confidence intervals, false-positive cost, regression and drift.
- Tenant secrets and private customer data never enter public repo, PR, model provider, telemetry or shared benchmark. Include deletion and retention contracts.
- Resource-aware tiers: Chromebook for orchestration/light synthetic tests; approved isolated GPU for larger experiments; zero-spend default.
- Independent verification and reproducible receipts are mandatory for promoted models.
- Avoid claiming a model is 'specialized' solely from prompting or marketing; label customization method and validated scope accurately.

## Initial deliverables (not yet implemented)
A. Registry schemas + validation tests with synthetic entries for existing Qwen, K2 Horizon 0.9B, Falcon-H1 0.5B.
B. Provider-neutral offline evaluation runner and comparison report with frozen synthetic invoice/contract/field-ticket cases.
C. Enterprise tenant-isolation contract and negative tests for data leakage.
D. Customization decision matrix and synthetic LoRA job manifest (no training run).
E. Independently reviewed model-promotion workflow and rollback test.

## Success criteria
Prove task-specific improvement against a frozen baseline, repeatability, independent evidence, tenant isolation, legal permission, and acceptable latency/cost. If a candidate fails, reject it. Preserve THE BIG ONE as private real-company audit validation data, not general training material.

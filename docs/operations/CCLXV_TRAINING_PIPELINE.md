# CCLXV training pipeline

Tested code `cfbf5386e679696048318ad843aeb29b520654bb`.

`aurex/model_lab.py` validates a training manifest and never starts a job. A job is refused when the dataset is not `SYNTHETIC_ONLY`, the base revision is missing, the license is not reviewed, the train, validation, and test splits are incomplete, the leakage check is not `PASS`, the budget is not zero, or the owner flag is absent.

When every gate passes, the decision is `READY_NOT_LAUNCHED` and `launch` stays `NOT_STARTED`. No PEFT, TRL, or Unsloth package was added. No adapter was trained.

Retrieval cites a document only for text that is not an instruction line. If the only matching line is an instruction such as "ignore prior instructions," the result is `ABSTAIN`. Citations do not grant authority.

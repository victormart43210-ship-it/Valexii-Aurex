"""Actual optimizer/save/reload smoke on a random tiny Qwen2, never Qwen 0.5B efficacy."""

import math

import pytest

torch = pytest.importorskip("torch")
pytest.importorskip("peft")
pytest.importorskip("transformers")


def test_real_lora_optimizer_and_reload(tmp_path):
    from peft import PeftModel
    from tokenizers import Tokenizer
    from tokenizers.models import WordLevel
    from tokenizers.pre_tokenizers import Whitespace
    from transformers import PreTrainedTokenizerFast, Qwen2Config, Qwen2ForCausalLM

    from training.common import encode
    from training.train_lora import fit

    torch.set_num_threads(1)
    torch.manual_seed(42)
    vocab = {
        "<unk>": 0,
        "<pad>": 1,
        "</s>": 2,
        "user": 3,
        "assistant": 4,
        "Witness": 5,
        "missing": 6,
        "HOLD": 7,
    }
    backend = Tokenizer(WordLevel(vocab, unk_token="<unk>"))
    backend.pre_tokenizer = Whitespace()
    tok = PreTrainedTokenizerFast(
        tokenizer_object=backend, unk_token="<unk>", pad_token="<pad>", eos_token="</s>"
    )
    tok.chat_template = "{% for message in messages %}{{ message['role'] + ' ' + message['content'] + ' </s> ' }}{% endfor %}{% if add_generation_prompt %}{{ 'assistant ' }}{% endif %}"
    row = {
        "messages": [
            {"role": "user", "content": "Witness missing"},
            {"role": "assistant", "content": "HOLD"},
        ]
    }
    encoded = encode(row, tok, 64)
    assert encoded["labels"][0] == -100
    assert 7 in encoded["labels"]
    cfg = Qwen2Config(
        vocab_size=len(vocab),
        hidden_size=32,
        intermediate_size=64,
        num_hidden_layers=1,
        num_attention_heads=2,
        num_key_value_heads=2,
    )
    model = Qwen2ForCausalLM(cfg)
    params = {
        "seed": 42,
        "rank": 2,
        "alpha": 4,
        "max_length": 64,
        "max_steps": 2,
        "learning_rate": 0.001,
        "use_cpu": True,
    }
    metrics = fit(model, tok, [row], params, tmp_path / "adapter")
    assert math.isfinite(metrics["train_loss"])
    assert (tmp_path / "adapter/adapter_model.safetensors").exists()
    loaded = PeftModel.from_pretrained(Qwen2ForCausalLM(cfg), tmp_path / "adapter")
    assert any(torch.count_nonzero(p) > 0 for n, p in loaded.named_parameters() if "lora_B" in n)
    loaded.merge_and_unload().save_pretrained(tmp_path / "merged", safe_serialization=True)
    assert (tmp_path / "merged/model.safetensors").exists()

"""Assistant-token masking on a tiny chat template. No foundation weights."""

import pytest

torch = pytest.importorskip("torch")
pytest.importorskip("transformers")


def tokenizer():
    from tokenizers import Tokenizer
    from tokenizers.models import WordLevel
    from tokenizers.pre_tokenizers import Whitespace
    from transformers import PreTrainedTokenizerFast

    vocab = {
        "<unk>": 0,
        "<pad>": 1,
        "</s>": 2,
        "user": 3,
        "assistant": 4,
        "system": 5,
        "Witness": 6,
        "missing": 7,
        "HOLD": 8,
        "again": 9,
    }
    backend = Tokenizer(WordLevel(vocab, unk_token="<unk>"))
    backend.pre_tokenizer = Whitespace()
    tok = PreTrainedTokenizerFast(
        tokenizer_object=backend, unk_token="<unk>", pad_token="<pad>", eos_token="</s>"
    )
    tok.chat_template = (
        "{% for message in messages %}"
        "{{ message['role'] + ' ' + message['content'] + ' </s> ' }}"
        "{% endfor %}"
        "{% if add_generation_prompt %}{{ 'assistant ' }}{% endif %}"
    )
    return tok


def test_multiturn_loss_is_assistant_only():
    from training.common import collator, encode

    tok = tokenizer()
    row = {
        "messages": [
            {"role": "system", "content": "Witness"},
            {"role": "user", "content": "missing"},
            {"role": "assistant", "content": "HOLD"},
            {"role": "user", "content": "again"},
            {"role": "assistant", "content": "HOLD"},
        ]
    }
    encoded = encode(row, tok, 64)
    assert encoded["labels"].count(8) == 2
    assert encoded["labels"][0] == -100
    assert 6 not in encoded["labels"]
    padded = collator(tok)([encoded, {"input_ids": [3], "attention_mask": [1], "labels": [3]}])
    assert int(padded["labels"][1, -1]) == -100
    assert int(padded["labels"][0, 0]) == -100


def test_overlength_malformed_and_unsupervised_rows_are_rejected():
    from training.common import encode

    tok = tokenizer()
    row = {
        "messages": [
            {"role": "user", "content": "Witness missing"},
            {"role": "assistant", "content": "HOLD"},
        ]
    }
    assert encode(row, tok, 64)["labels"]
    with pytest.raises(ValueError, match="max_length"):
        encode(row, tok, 2)
    with pytest.raises(ValueError, match="malformed"):
        encode({"messages": [{"role": "user", "content": "Witness"}]}, tok, 64)
    with pytest.raises(ValueError, match="malformed"):
        encode(
            {
                "messages": [
                    {"role": "user", "content": "Witness"},
                    {"role": "assistant", "content": "   "},
                ]
            },
            tok,
            64,
        )
    tok.chat_template = "{{ messages[0]['content'] }}"
    with pytest.raises(ValueError):
        encode(row, tok, 64)

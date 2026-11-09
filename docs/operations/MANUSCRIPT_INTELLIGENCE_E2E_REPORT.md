# Manuscript imaging end-to-end verification

**Offline historical image measurement passed. Scientific interpretation and hosted display remain open.**

Source is [Voynich folio 1r](https://commons.wikimedia.org/wiki/File:Voynich_Manuscript_(3).jpg), attributed to Yale's Beinecke Library on Wikimedia Commons and labeled a faithful reproduction of a public-domain work in the United States. The original JPEG downloaded from Commons was 1116×1536, SHA-256 `c0f11e98eb472063c812876a0dafec1e1344f0be92c7847e2e22e294b2253e17`. The image is not bundled in this repository.

The local run opened the JPEG with Pillow 13.0.0, converted to RGB, applied `thumbnail((512,512), Image.Resampling.LANCZOS)`, and encoded a 372×512 PNG. Derived SHA-256 `5608271b4b87a57b3e109ad9047781520ade4b5bbe1182cbebe19be356273ed9`. Two calls to `aurex.manuscript_forensics.pipeline.examine_bytes` returned identical reports with 11 layers and 24 retained pixel regions, the configured cap. They carried bounding boxes and digests. Region count is not a glyph count or a reading order.

`tests/test_manuscript_imaging.py` exercises PNG/JPEG, malformed and oversized input, capped processing, deterministic hashes and synthetic pixel controls. The existing invented-script control suite remains separate. Historical transcription, glyph recognition, entropy and language claims require evidence beyond these measurements. No hypothesis was promoted, no transcription returned, and decipherment remains NOT_CLAIMED. The recovered core has no website route, remote model or durable custody.

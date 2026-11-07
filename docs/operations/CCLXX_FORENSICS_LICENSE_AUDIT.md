# CCLXX forensics license audit

Code SHA `64dadbfd673186fbe65bc653a4658d866178ca8a`.

Pillow 13.0.0 is the only new package. Its installed metadata says `MIT-CMU`. The Pillow repository LICENSE on `main` is the same MIT-CMU notice. It is a required dependency, pinned `pillow>=13.0.0,<14`, because the previous 12.3.0 release was reported by Snyk as vulnerable and 13.0.0 was reported as not affected. That Snyk page is not an independent vulnerability scan.

Hoku 3.2 is GPL-2.0. The Early Manuscripts Electronic Library distributes it free of charge. That does not make it compatible with combining into this Apache-2.0 package. It was not downloaded. HyperSpy is GPL-3.0 and was not imported. Both are external adapters only: an operator may run them as separate programs. This repository does not call them.

Kraken is Apache-2.0 and eScriptorium is MIT. Their model files and training sets were not reviewed and were not downloaded. No recognizer is wired in, so the laboratory cannot present a model guess as writing.

OpenCV 4.5 and later is Apache-2.0. scikit-image is BSD-3-Clause with some BSD-2-Clause and MIT files. Spectral Python is MIT. Mirador is Apache-2.0. OpenSeadragon is BSD-3-Clause. Tesseract is Apache-2.0. None of those were installed.

The remaining named tools are `LICENSE_REVIEW_REQUIRED` because their license files were not opened in this session. They are not dependencies.

No paid API, model weight, or third-party dataset was fetched.

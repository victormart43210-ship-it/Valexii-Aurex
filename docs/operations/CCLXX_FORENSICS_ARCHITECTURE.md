# CCLXX forensics architecture

Code SHA `64dadbfd673186fbe65bc653a4658d866178ca8a`.

The laboratory is `aurex/manuscript_forensics/`. It is mounted at `/v1/manuscript-forensics` behind the existing service bearer. It does not import DISPATER and it does not write a financial record. `AUREX_MANUSCRIPT_FORENSICS=enabled` is required. Without that variable the examine route returns HTTP 403.

The public page is `/research/manuscript-forensics`. It asks the server to examine one of four synthetic fixtures. The browser does not receive the service token. The opacity slider changes CSS only. The downloaded JSON is the API report, including source and layer SHA-256 values, parameters, and limitations.

Tier 1, in this process:

- Admit PNG, JPEG, or a single-frame TIFF up to 1,500,000 bytes and 512 pixels on a side.
- Refuse PDF rasterization, an unknown type, a declared type that does not match the magic bytes, a decompression bomb, and more than one frame.
- Keep the admitted bytes. Derived PNGs are new files with their own digests.
- Grayscale, three channels, contrast stretch, background residual, adaptive threshold, 3x3 median, gradient, and a morphological close.
- Connected components of at least 12 ink pixels, labeled `UNVERIFIED_COMPONENT`, with `reading: null`.
- For supplied bands of equal size: a difference, a guarded ratio, an index or caller-asserted false-color composite, and one principal component.
- An integer shift of at most 4 pixels when alignment is requested. Pixels with no source sample are 0 and counted as absent. Different band sizes are refused rather than resampled.
- Research templates for Voynich, Rongorongo, Linear A, palimpsests, and artworks. Each says `NOT_ESTABLISHED`.

Tier 2 and tier 3 are off. Kraken, Spectral Python, Hoku, HyperSpy, RTI, photogrammetry, and X-ray toolkits are not imported. An ordinary RGB image is not given a wavelength, and it is not treated as an infrared or X-ray capture.

XAELI is not called by this route. If the private model is down, the imaging measurements still run.

The response effect is `NONE`. `recovered_text` is null. `decipherment` is `NOT_CLAIMED`. A request whose effect is not `NONE` is refused before any image is produced. `dataset_type` must be `SYNTHETIC_ONLY`.

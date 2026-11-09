# KUSANAGI XCVII — APIS PRIME FOLIO INDEX
## One archival order, one reasoning spine, evidence-first authority

**STATUS: SOURCE-ONLY DESIGN + BOUNDED OFFLINE LIBRARY PROTOTYPE; DRAFT / HOLD (2026-10-18).**

Owner request: combine the organizational practices associated with the Vatican Library, Ramon Llull's combinatorial method, medieval cryptanalysis, astrolabe makers, the archived research of Nikola Tesla, and the **2026 Maya calendrical epigraphy result** into the existing AUREX/OX ordering architecture. This is an engineering *analogy*, not an adoption of religious, historical, or museum proprietary cataloguing systems. Keep all 14 APIS PRIME names, **one reasoning spine, zero new tabs**, and the existing production evidence/authority boundaries.

## What historically supports the choices

| Historical material | What is actually documented | Useful software principle; not a claim of historical software |
| --- | --- | --- |
| **Vatican Apostolic Library** | Collection-level catalogues for manuscript, archive, printed and other material; authority files; source identifiers (shelfmarks); IIIF-linked digitized material and annotations. | Permanent accessions, collection hierarchy, canonical names/aliases, links to page/folio/image coordinates. **Keep the physical/scholarly shelfmark distinct from the immutable AUREX accession and the SHA-256 content fingerprint.** |
| **Ramon Llull (1232–1316)** | Ars: concepts, relations, questions, diagrams and rotating combinations; letter semantics depend on their **figure/context**. | Typed object/relationship/question facets, explicit alternative reasoning paths and bounded combinatorial queries. No universal cryptographic decipherment asserted. |
| **Al-Kindi (9th century); Ibn Adlan (13th century)** | Historical frequency analysis, letter-order constraints and cryptanalytic hypotheses; these authors were **not** exact contemporaries of Llull. | Statistical sidecar analyses, corpus/sampling sufficiency, alternative cipher candidates and negative controls; frequency matches never override source metadata. |
| **Astrolabe history** | Greek stereographic foundations; successive development by astronomers and instrument makers in Islamic lands and medieval Europe, notably al-Zarqali and other creators. Not one inventor. | **Separate reference frames**: raw observed instant, local recorded time, source calendar, coordinate system, timezone, epoch and calibration/assumptions. Never silently use modern Gregorian dates for an ancient inscription. |
| **Nikola Tesla archive** | Museum preserves separately categorized scientific notes, patents, diagrams, correspondence, and finances; chronology and multiple patent jurisdictions matter. | Preserve sketches/source material apart from experiment revisions, measurements, failed tests, apparatus/calibration, repeatable procedures and invention/patent families. Distinguish **a proposal from a measured experiment**. |
| **2026 Maya El Palmar Stela 46** | June 2026 peer-reviewed archaeological/epigraphic research used 3D scanning, photogrammetry and contextual comparison to read **Long Count 8.7.1.0.0** (180 CE) on damaged Stela 46, currently earliest known from Maya lowlands. | Preserve raw scans, capture method, glyph regions, transcription candidates, calendrical arithmetic, independent archaeological context and uncertainty; consistency with 260-day cycles is **not enough to choose one reading**. |

**References (institutional / scholarship):**
- Vatican Apostolic Library: https://www.vaticanlibrary.va/en/home.php ; manuscript division https://bav.vatican.va/en/the-collections/manuscript-department.html ; catalog https://opac.vatlib.it/ ; IIIF https://digi.vatlib.it/
- Ramon Llull, Stanford Encyclopedia of Philosophy: https://plato.stanford.edu/entries/llull/
- Al-Kindi / cryptology historical background: https://web.cecs.pdx.edu/~dmcgrath/courses/F26/introsec/history-of-cryptography.html
- Museo Galileo, Astrolabe history and al-Zarqali: https://catalogue.museogalileo.it/indepth/Astrolabe.html ; Oxford History of Science Museum https://www.hsm.ox.ac.uk/science-islamic-world
- Nikola Tesla Museum archive https://tesla-museum.org/en/legacy/archive/ and invention grouping https://tesla-museum.org/en/legacy/archive/activity/
- **Primary 2026 scholarship** Tsukamoto et al., *Ancient Mesoamerica*, published June 5, 2026, https://doi.org/10.1017/S0956536126100984

**Critical historical distinction:** The 2026 result was **a new reading of an early Maya monument**, not a first decipherment of the entire Maya calendar, not proof that the 260-day count was invented in 2026, and not evidence that AUREX made this scholarly discovery. The 260-day calendar continues in some Maya communities; treat historical and contemporary cultural knowledge respectfully and accurately.

## Single canonical ordering flow

```text
               ONE USER INPUT / CONSENT / TENANT BOUNDARY
                               |
  ORIGINAL SOURCE (immutable bytes in a separately approved vault)
                               |
   VATICAN: accession + collection + shelfmark + authority metadata
                               |
       CAPTURE: scan/IIIF canvas/folio/line or file/repository path
                               |
   ASTROLABE: source-date + UTC ingest timestamp + units/coordinate frame
                               |
     DERIVATIVE: extraction → transcription → normalization
                               |
     LLULL: entities + relations + constrained question index
     AL-KINDI: frequencies + cryptanalytic candidates + null tests
                               |
  TESLA: hypothesis → experiment → results/failed controls → revisions
                               |
  MAYA: chronological/calendar consistency, MULTIPLE candidates retained
                               |
            APIS PRIME ONE REASONING SPINE (14 roles)
                               |
     Source → Claim → Challenge → Evidence → Qualified finding
                               |
           CUSTOS / SHRIKE / Independent human review
                               |
             NOW → CHANGED → NEXT → WHY → PROOF
                               |
                  ONE OWNER VIEW / XAELI
```

Logical pipeline, **not** 14 tabs, 14 agents, or a mandate to run all techniques on every input. Financial invoices should not be subjected to Maya calendar conversion, and manuscript fragments should not receive financial audit verdicts.

### Identifier discipline — no overloaded primary keys

- **Accession ID**: internal stable object identifier, tenant-scoped. Never repurpose or silently rename.
- **Collection / source shelfmark**: human archival reference; can describe external museum manuscript material. Never rely on shelfmark alone for uniqueness.
- **SHA-256 fingerprint**: source/derived bytes digest; detects changes, not authorship, authenticity, or financial legitimacy.
- **Provenance**: original creator/holder, date, acquisition permission/license, capture method, page/canvas, transformation software version and source links. The current prototype only stores bounded *metadata*, not complete archival provenance.
- **Version / parent link**: new extraction/transcription is a new object linked to its original. A correction does not rewrite an old historical source.
- **Domain and visibility**: research/manuscripts, finance, compliance, code, model. Both public/private share **schema**, not customer data or free-form access.
- **Calendar/clock**: preserve the original notation separately from normalized UTC/event time, with explicit dating method, timezone, units and correlation assumption. Ancient dates may be uncertain.

### Temporal counterexample from 2026 Maya research

AUREX's `maya_long_count_days` computes **only relative integers** in the mixed-radix system (1 k'in/day; 20 k'in/winal; 18 winal/tun; 20 tun/k'atun; 20 k'atun/b'ak'tun).

Test **synthetically proposed alternate readings** of an eroded inscription:
- `8.7.0.5.0`
- `8.7.1.0.0`
- `8.7.1.13.0`

The neighboring candidate values differ by **260 days** and share the same residue modulo 260. Thus the Tzolk'in phase **cannot uniquely distinguish them**; the analyzer outputs `AMBIGUOUS_READING_HOLD`. This is a **mathematical test case**, not a claim that all three readings are equally supported by the published 2026 study. A scholarly reading needs actual glyph evidence, archaeological context and independent review. No automatic Julian/Gregorian conversion or “Maya prophecy” speculation.

## Across existing AUREX domains

| Input | Canonical original evidence | Typed relationships | Independent checks (domain-specific) |
| --- | --- | --- | --- |
| Ancient manuscript | archive/shelfmark, manuscript page, scan, transcription | glyph segment → candidate transcription → hypothesis | image/source alignment; calendar consistency; held-out controls; specialist review |
| Company invoice/PO/field ticket | explicit tenant-controlled originals + approvals | invoice line → PO item → field ticket → payment | exact decimal/unit reconciliation, missing signatures, period cutoffs, inconsistent records; accountant review |
| IRS/DOT/insurance response | permitted source policies/documents and retention proofs | requirement → source → claimed compliance → contradiction | jurisdiction/period, expiration, independent human legal/accounting review. **No guarantee of compliance.** |
| Python/repository code | immutable file and commit SHA, path, dependency manifests | AST node → definition/import → test → failure evidence | static AST, isolated approved reproducibility test, pinned build and security review |
| LLM evaluation/training | dataset license, consent, prompt/test lineage | sample → training/eval split → outcome → independent scorer | contamination/leakage and held-out tests; **do not train on private data by default** |

Same metadata contract, distinct access rights and evidentiary methods. **Do not merge all user documents into a single public semantic index.** Segregate by tenant and authorization; access decisions occur at the authenticated service boundary *before* model prompting, search, embedding, indexing or export. No customer financial content enters training without a distinct, revocable opt-in process and applicable legal requirements.

## What is implemented by this PR

- `aurex/folio_index.py`: offline in-memory metadata registry prototype; source SHA, named accession, provenance shelfmark, collection, immutable source/derived linkage, tenant and public/private classification, controlled link relations; **one 260-day Maya alternative hypothesis negative control**.
- `tests/test_folio_index.py`: synthetic positive/negative tests for immutability, tenant isolation, private-to-public leakage, reference completeness, data/consent validation and calendrical ambiguity.
- This design document.

**Not implemented:** a durable object vault, complete OCR/IIIF ingestion, a full semantic search index, RBAC, GDPR/compliance retention, actual Vatican catalog integration, archaeological 3D pipelines, a cryptanalysis suite, patent-claim engine, LLM training, a deployed API route, Cloudflare Worker changes, public/private portal, Lovable UI, or production financial audit. No actual manuscript decoded. Only these **schema and bounded indexing foundations** are introduced. Operational code stays in the existing AUREX repository, not a parallel backend.

## Gates to production

1. Freeze schema/cross-domain provenance under independent reviewer; verify on **exact reviewed SHA** with offline pytest, Ruff, strict Mypy, compileall and existing AUREX suite.
2. Test adversarial tenanted catalogs, identifier collisions, orphan lineage, invalid date units/timezone, contaminated OCR, duplicate documents, forged SHA descriptions and privacy exposure. Storage must have **real authenticated authorization** and tamper-evident event history; the in-memory prototype has neither.
3. Only after review, reconcile the correct subset of existing draft PRs #80 (financial), #84–86 (Qwen/APIS spine) onto a fresh protected-main base **without wholesale merging or downgrading mainline safeguards**. Create proof of one private synthetic invoice/PO/ticket workflow and one public manuscript example separately.
4. Review explicit source licensing and Indigenous cultural context, especially for Maya materials. Vatican and museum archival items can have distinct rights; an available digitized page is not automatically licensed for AI training.
5. Update one owner-only **AUREX/OX existing panel**, no 14 tabs. No false 100% bar; readiness ladder tracks code → CI → deployment → independently verified end to end.
6. Production/cloud effects remain **HOLD** until separate owner decision. External spend $0. AUREX research conclusions have **authority NONE**; enterprise regulatory/financial consequences require qualified human reviewers.

**Doctrines:** Evidence → Qualification → Reality → Authority → Effect; ROTAS reverse auditing; the system is never its own sole witness; unknown ≠ safe; historical truth vs present authority must remain separate. **No merge, public/private service deployment or Lovable edits authorized by this design lock.**

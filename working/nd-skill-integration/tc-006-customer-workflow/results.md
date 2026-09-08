# TC-006 Results — Customer ND Pattern Discovery + Verification

## Test status

```text
PASS
```

## Execution summary

TC-006 was executed as a **controlled workflow emulation** rather than an exact reproduction of the customer's Linux orchestration.

Two isolated Cursor 3.18.25 conversations were used:

1. **TC-006A — Discovery:** customer `nd-code-analyzer` methodology + customer ND Pattern Catalog + CoreStory application intelligence.
2. **TC-006B — Verification:** clean Cursor context receiving only the discovery artifact, then applying `prove-nd` + `prove-nd-mt` + CoreStory.

The original customer `create-cli-agent` / `cursor-agent` infrastructure and exact requested model combination were not reproduced. These are workflow-fidelity deviations and are not attributed to CoreStory.

Token metering is out of scope for this test.

## TC-006A — Discovery

### Result

**PASS**

The customer ND pattern catalog drove broad MT/concurrency discovery without a preselected candidate or mechanism. The original `scan_nd.py` implementation was not present, so the mechanical discovery stage was emulated from the catalog patterns using local search. The customer pattern knowledge remained the basis of discovery.

CoreStory project `cts-code` (id 10), conversation 82, was used to add application-level context including MT dispatch surfaces, GLS/lazyTNS/fmax relationships, threading controls, callers, downstream consumers, and candidate qualification.

### Discovery artifact

`results/nd_mt_candidates_discovery.md`

The artifact preserved **10 candidates** for isolated verification. Each candidate included:

- pattern/catalog mechanism,
- file/function/symbol,
- reason for the match,
- possible MT reachability,
- shared/mutable state,
- downstream/observable evidence where available,
- controls/neutralizers,
- missing evidence,
- CoreStory relationships for the verifier to validate.

No candidate was presented as a proven Real ND defect.

### Discovery candidates

| ID | Discovery mechanism / focus |
|---|---|
| C1 | Lazy mutable `dosMap` cache on const path |
| C2 | Lazy phase-delay cache / concurrent-map compound operation |
| C3 | Shared SCC cache check-then-act under MT |
| C4 | Boolean `parallel_reduce` / schedule early-exit |
| C5 | `hardware_concurrency`-dependent grain sizing |
| C6 | Fmax parallel partition + floating-point TNS fold |
| C7 | Concurrent-vector arrival collection / median path |
| C8 | lazyTNS per-thread gather + serial merge |
| C9 | DRC concurrent-hash-map find/insert path |
| C10 | Mutable GLS collect-SCLK cache |

The discovery pass also explicitly recorded no useful hits for catalog classes 4.3, 4.5, and 4.6 in this scope.

## Discovery -> verification handoff

```text
Handoff method: manual clean-context emulation
Clean verifier context: YES
TC-006A conversation exposed to verifier: NO
TC-001..TC-005 findings exposed: NO
Coverity / hidden ground truth exposed: NO
Discovery artifact passed unmodified: YES
```

Only `nd_mt_candidates_discovery.md` plus the verification instruction was supplied to the clean verifier.

## TC-006B — Verification

### Result

**PASS**

The verifier read the customer `prove-nd` and `prove-nd-mt` methodology, used CoreStory project `cts-code` conversation 83, and performed targeted source/caller validation.

No candidate among C1-C10 was proven Real for equivalent-run MT nondeterminism. The verifier preserved non-Real classifications rather than promoting suspicious syntax.

### Final classifications

| ID | Classification | Verification result |
|---|---|---|
| C1 | Dead/unused — MT-unreachable | Unsafe-looking lazy `dosMap`, but no proven worker-body caller |
| C2 | Latent-only — Race-but-idempotent | MT path established; surrounding accessor/concurrent-map behavior and no divergent phase/cost proof prevented elevation |
| C3 | Latent-only — Race-but-idempotent | MT populate established; disjoint bags and deterministic assembly neutralize insertion-order concern |
| C4 | Latent-only | Boolean AND/OR associative; variable early exit not shown to change application result |
| C5 | False positive | Hardware concurrency affects grain only; indexed outputs are disjoint |
| C6 | Latent-only | FP association can vary with configured thread count, but fixed-thread equivalent-run schedule ND was not established |
| C7 | Neutralized | Concurrent insertion order is discarded by the `std::set` median calculation |
| C8 | Latent-only | Parallel per-thread gather followed by deterministic thread-index merge |
| C9 | Latent-only — Race-but-idempotent | Strongest confirmed concurrent-writer case; concurrent-map accessor serializes and same-key values are expected identical |
| C10 | Dead/unused — MT-unreachable | Lazy cache is used during sequential preparation rather than worker execution |

### Findings summary

```text
Real:            0
Neutralized:     1  (C7)
Latent-only:     6  (C2, C3, C4, C6, C8, C9)
False positive:  1  (C5)
Dead/unused:     2  (C1, C10)
Unresolved:      0 as final classification; individual missing-evidence items remain documented
```

## CoreStory contribution

CoreStory contributed application intelligence in both phases rather than replacing the customer ND knowledge.

Observed contribution included:

- locating and validating MT dispatch/execution surfaces,
- connecting candidate code to GLS, CTO, lazyTNS, fmax, and QoR paths,
- tracing callers and downstream consumers,
- identifying controls such as `isUseClockGroupLatencyMT`, `large_skew_group_limit_for_threading`, `enable_cto_mt_task`, `isQorTblUseDrcCache`, and max-thread APIs,
- helping distinguish worker-reachable from sequential-only candidates,
- identifying deterministic assembly/merge behavior and other potential neutralizers,
- providing relationships that were then checked against targeted local source.

The verifier still performed local source/caller sweeps where direct code evidence was required. Some implementations and customer-environment tools were unavailable locally, and those limitations were documented rather than inferred through.

## Cross-phase assessment

```text
Customer ND knowledge preserved:                     YES
Broad catalog-guided discovery performed:            YES
CoreStory contributed during discovery:              YES
Candidate handoff was concrete/usable:                YES
Verifier context was isolated:                        YES
prove-nd proof discipline preserved:                  YES
prove-nd-mt proof discipline preserved:               YES
MT reachability investigated:                         YES
Downstream consequence investigated:                  YES
Neutralizers/canonicalization investigated:           YES
Unsupported Real findings avoided:                    YES
Workflow/model deviations recorded:                   YES
Exact customer scanner/orchestration reproduced:      NO
```

## Test verdict

```text
PASS
```

### Rationale

TC-006 established that the customer's ND pattern knowledge can drive broad MT/concurrency candidate discovery while CoreStory adds application-level context for reachability, relationships, downstream observability, controls, and neutralizers. A clean verifier was able to consume the discovery artifact and apply the customer's `prove-nd` / `prove-nd-mt` discipline without relying on hidden discovery context.

The workflow reduced a broad candidate set to evidence-backed classifications and did not manufacture Real findings when the causal proof was incomplete.

A Real finding was not required for this workflow-validation test.

## Interpretation boundary

This was a **controlled workflow emulation**, not an exact reproduction of the customer's `create-cli-agent`, `cursor-agent`, model stack, scanner implementation, or complete internal development environment.

TC-006 does **not** establish recall, precision, or defect coverage against Coverity. It establishes workflow compatibility and evidence discipline.

## Next step / stop condition

**No additional synthetic ND tests are planned at this time.**

TC-001 through TC-005 validated mechanism-specific verification behavior. TC-006 validated broad customer-pattern discovery plus isolated verification. Together these provide sufficient workflow-validation evidence for the current stage.

The next evaluation phase is the customer ground-truth benchmark and is intentionally blocked pending the Coverity findings expected from Scott, including:

- `POINTER_NONDETERMINISM`
- `UNINIT`
- `UNINIT_CTOR`

When those findings are available, use them as hidden/controlled ground truth to evaluate recall, false positives, candidate qualification, and any additional supported findings. Do not add further synthetic tests before that benchmark unless new customer feedback identifies a specific workflow gap.
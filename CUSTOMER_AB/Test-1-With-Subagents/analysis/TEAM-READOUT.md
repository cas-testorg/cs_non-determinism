# Test 1 Team Readout — Customer A/B Non-Determinism Evaluation

**Test:** Test 1 — With Subagents  
**Status:** Preliminary technical readout; SME/runtime validation remains pending  
**Purpose:** Internal discussion of what Test 1 actually tells us about the existing Synopsys workflow and the CoreStory-assisted workflow.

## Executive summary

The initial Test 1 comparison appears unfavorable to the CoreStory-assisted arm if we look only at the promoted-finding counts and the customer's first source adjudication. The existing workflow promoted 19 findings and the CoreStory-assisted workflow promoted 6. The customer's comparison initially identified 9 source-confirmed unique ND candidates, with 8 found by the existing workflow and 4 found by the CoreStory-assisted workflow.

However, four focused independent investigations materially change how those numbers should be interpreted.

We selected representative disagreements from Test 1 and re-investigated them using a fixed configuration: Cursor, Claude Opus 4.8 / High thinking, CoreStory MCP enabled against project 10 (`cts-code`), no CoreStory ND rule, none of the customer ND discovery/proof skills, and only the `agentic-bug-resolution` playbook. The previous A/B conclusions were withheld from these investigations.

The focused work shows that some apparent "misses" are actually qualification disagreements. Of the four cases investigated:

| Candidate | Initial A/B appearance | Focused result |
| --- | --- | --- |
| `soSolverUpdater.cc:2100` | Existing workflow found it; CoreStory-assisted missed it | Reported data race is **not substantiated** by the focused source investigation; residual C++ library/runtime question remains |
| `msDrivers.cc:711` | CoreStory-assisted only | **Source-substantiated latent ND** with a credible path through specific MLPH/auto-tap consumers; runtime trigger conditions remain |
| `ccdcgSolver.cc:501` | Existing workflow promoted; CoreStory-assisted dismissed | Focused investigation **supports dismissal** of the RNG mechanism; fixed seed + immediate reseed + sequential consumption |
| `msuiGetPowerTaps.cc` | CoreStory-assisted promoted; later source review rejected | Promotion is **not substantiated**; workflow inferred pointer-address hashing without resolving the container implementation |

The key takeaway is therefore not simply "CoreStory had lower recall." Test 1 shows a mixture of discovery differences, qualification differences, and evidence-gating failures. The original 9-issue source-reviewed union should not yet be treated as final ground truth.

## What the original A/B showed

The customer-controlled comparison reported:

| Metric | Without MCP | With MCP |
| --- | ---: | ---: |
| Promoted findings | 19 | 6 |
| Source-confirmed unique findings in initial comparison | 8 | 4 |
| Coverage against initial 9-issue source-reviewed union | 89% | 44% |
| Promoted findings surviving that source review | 8/19 | 4/6 |

On that initial adjudication, the existing Synopsys workflow demonstrated substantially broader discovery. It found candidates the CoreStory-assisted workflow did not, including the reported `soSolverUpdater` race, auto-balance feedback, hash-to-floating-point behavior, keepout behavior, and endpoint priority behavior.

The CoreStory-assisted workflow produced a much shorter list, but the shorter list was not automatically higher quality: two of its six promoted findings did not survive the customer's later source review.

These are real Test 1 observations. We should not minimize them.

## Why we performed the focused investigations

The comparison report itself re-read source to adjudicate disagreements, but nothing was built or runtime-reproduced. Its "Confirmed" designation therefore means source-confirmed rather than runtime-confirmed.

We wanted to answer a more specific question:

> Are the A/B differences primarily discovery failures, or are some of them different qualification decisions that require deeper application tracing?

The four investigations intentionally removed the original ND workflow from the equation and used the same independent investigation configuration for every candidate.

The investigation path was:

`reported construct → mechanism → build inclusion → production reachability → runtime/configuration → propagation → neutralization → observable consequence → disposition`

## Focused Investigation 01 — `soSolverUpdater.cc:2100`

### Initial interpretation

This initially looked like one of the strongest CoreStory recall failures. The existing workflow promoted it as a TBB/`std::map::operator[]` data race, the CoreStory-assisted workflow did not report it, and the customer's source comparison called it a real data race.

### Focused result

The independent investigation confirmed that the code is built and production reachable, but found evidence that materially weakens the reported race mechanism:

- relevant map keys are prepopulated before the parallel region;
- solver outer maps are explicitly initialized single-threaded;
- workers operate on distinct scenario values/inner maps;
- setup and hold processing are separate;
- downstream consumers execute after the parallel join;
- no credible concurrent structural mutation was demonstrated.

A narrow technical question remains around the C++ standard guarantees for concurrent existing-key `std::map::operator[]` access and the production STL implementation. TSan/runtime confirmation is still appropriate.

### Current interpretation

**Adjudication disagreement requiring SME/runtime validation — not a clean CoreStory discovery miss.**

The fact that the With-MCP arm did not report this candidate should no longer be counted as an established recall failure until the race itself is validated.

## Focused Investigation 02 — `msDrivers.cc:711`

### Initial interpretation

This was a CoreStory-assisted-only finding.

### Focused result

The independent investigation substantiated the mechanism at source level:

- `findDriverTerm` iterates a raw-pointer `std::set<ndmNet*>`;
- default pointer ordering controls which element is processed last;
- the scalar return is therefore last-wins and potentially address-order dependent;
- the separately accumulated `drvTerms` set uses a stable comparator and is not itself the problem;
- most callers neutralize the scalar behavior by discarding it or re-deriving the driver;
- three MLPH/auto-tap callers consume the scalar result directly;
- those paths provide a credible propagation path into clock/sink selection and potentially topology/QoR.

The behavior is gated: MLPH must be enabled, the load-net set must contain multiple entries, and the relevant leaf-level/consumer conditions must occur.

### Current interpretation

**Source-substantiated latent nondeterminism, pending runtime confirmation of trigger conditions.**

This is a good example of why caller and propagation tracing matter. The suspicious helper is not globally defective; most callers neutralize the behavior. The defect becomes meaningful only for a small set of consumers.

## Focused Investigation 03 — `ccdcgSolver.cc:501`

### Initial interpretation

The existing workflow promoted use of `srand()/rand()`; the CoreStory-assisted workflow dismissed it. The customer comparison agreed with the dismissal.

### Focused result

The independent investigation strongly supports the dismissal:

- `srand(100)` uses a fixed literal seed;
- it occurs immediately before the consumption loop;
- `rand()` is consumed sequentially;
- no relevant concurrent production RNG consumer was identified;
- prior global RNG state is irrelevant because the code reseeds immediately;
- the generated sequence is therefore deterministic by candidate index.

There is a legitimate residual question: if the upstream candidate-to-index mapping is itself nondeterministic, the deterministic perturbation could be applied to different candidates. In that case this code would amplify upstream ND rather than create it.

### Current interpretation

**Reported RNG defect is not substantiated. Investigation should move upstream to candidate ordering if we want to pursue the residual risk.**

This is the clearest focused example of a useful qualification decision in the CoreStory-assisted arm.

## Focused Investigation 04 — `msuiGetPowerTaps.cc`

### Initial interpretation

The CoreStory-assisted workflow promoted this as pointer-address-driven iteration nondeterminism. The customer source comparison later rejected that interpretation.

### Focused result

The structural pattern exists:

`dosUnorderedSet<ndmBlkInst*> → iteration → unsorted vector → Tcl collection`

But the critical mechanism was not proven.

The actual `dosUnorderedSet` / `dosContainer::keyHash` implementation is outside the available CTS source and CoreStory index. Adjacent source conventions indicate that NDM pointer hashing/comparison is based on object identity such as `ndmID`/`ndmType`, not necessarily raw address.

The downstream `clct_list_to_collection` implementation is also unavailable, so we cannot establish whether it preserves or canonicalizes order.

### Current interpretation

**Unsubstantiated on current evidence.**

This exposes an important workflow failure: the With-MCP path appears to have moved from "unordered container containing pointers" to "pointer-address-based unstable ordering" without resolving the implementation required to support that conclusion.

The correct disposition at that point should have been **UNRESOLVED — container semantics required**, not promotion as a real ND defect.

## What Test 1 is telling us

### 1. The existing Synopsys workflow is strong at broad ND candidate discovery

The original A/B result demonstrates that it explored a wider set of potential mechanisms and promoted substantially more candidates. We should treat that as a real strength.

### 2. Promoted-finding count is not the same as validated-defect recall

Investigation 01 is the clearest warning. A candidate counted as a CoreStory miss in the initial comparison may itself have been over-promoted.

Until SME/runtime adjudication is complete, "8 versus 4" is best described as coverage against the customer's **initial source-reviewed union**, not final defect recall.

### 3. Application qualification can materially change disposition

Investigations 01–03 show the value of asking questions beyond the local suspicious construct:

- Is it actually built?
- Is it production reachable?
- Under what configuration?
- Does the suspected mechanism really vary?
- Which callers preserve it?
- Which callers neutralize it?
- Does it reach an observable consequence?

That is where some of the most useful differentiation is appearing.

### 4. Application context does not eliminate bad source inference

Investigation 04 is equally important. Having application context available does not guarantee correct qualification.

If a load-bearing implementation cannot be resolved, the workflow must stop at **UNRESOLVED** rather than substitute an assumption.

### 5. The A/B is currently testing more than CoreStory

Test 1 compares two end-to-end workflows, not an isolated "CoreStory context on/off" variable. Discovery behavior, orchestration/subagents, model routing, skills, and qualification behavior can all affect the final lists.

That limits causal claims about MCP itself.

## Emerging workflow model

The evidence suggests a potentially better division of labor than asking CoreStory to replace a mature ND discovery workflow:

```text
Broad ND discovery / mechanism detection
                ↓
        candidate set
                ↓
Application qualification
  - build inclusion
  - production reachability
  - runtime/config gates
  - exact mechanism
  - callers and propagation
  - neutralization
  - observable consequence
  - unresolved evidence
                ↓
          SME review
                ↓
      validated defect
                ↓
impact analysis / remediation
```

The next experiment should consider freezing the candidate set and comparing the existing proof/qualification process with CoreStory-assisted application qualification. That would isolate the part of the workflow where the focused investigations are showing the most interesting signal.

## Proposed qualification gate

A candidate should not be promoted merely because it matches a known ND pattern.

For each candidate:

1. Confirm build inclusion.
2. Confirm production reachability.
3. Establish the runtime/configuration gate.
4. Prove the exact ND mechanism.
5. Establish the source of varying input/order/state.
6. Trace propagation through production callers.
7. Look explicitly for neutralizers.
8. Establish a credible observable consequence.
9. If a load-bearing implementation is unavailable, classify **UNRESOLVED**.
10. Promote only when the evidence chain supports the disposition.

This directly addresses the failure seen in `msuiGetPowerTaps`.

## Questions for the team

For the discussion, the highest-value questions are:

1. Do we agree that the 9-candidate source-reviewed union should remain provisional until SME/runtime review?
2. Should `soSolverUpdater` be removed from the "CoreStory recall miss" bucket pending TSan/SME confirmation?
3. Does `msDrivers.cc:711` represent the kind of application-level qualification value we want CoreStory to provide?
4. Should unresolved external implementations automatically prevent promotion to a confirmed finding?
5. Can we inspect the original tool/subagent traces to determine whether CoreStory evidence actually caused the successful and unsuccessful decisions, rather than attributing them to the entire With-MCP workflow?
6. For the next iteration, should we freeze a candidate set and compare qualification quality separately from discovery recall?

## Current conclusion

Test 1 does **not** support a claim that CoreStory improves broad ND discovery. The original A/B result favors the existing Synopsys workflow on discovery coverage against the initial source-reviewed union.

But the focused investigations also show that the raw A/B counts do not tell the whole story. At least one apparent CoreStory miss is now an unresolved adjudication disagreement; one CoreStory-only candidate survives deep source qualification; one CoreStory dismissal is strongly supported; and one CoreStory-assisted promotion exposes a concrete evidence-gating failure.

The strongest hypothesis coming out of Test 1 is therefore:

> **CoreStory's differentiated role may be application-level qualification between broad ND detection and expensive SME review, rather than replacement of Synopsys' existing ND discovery capability.**

That hypothesis is not proven by Test 1. It is the next thing we should isolate and measure.

## Claim boundaries

- No Test 1 finding has been runtime reproduced by this evaluation.
- The customer's 9-issue union is source-reviewed, not final SME/runtime ground truth.
- The focused investigations are independent source/application investigations, not reproductions of either original A/B arm.
- We should not attribute a result specifically to CoreStory MCP unless execution evidence shows CoreStory information materially influenced that decision.
- Token/runtime/cost comparisons should remain secondary until workflow/model/subagent configuration is controlled.

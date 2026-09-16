# TC-001B — CoreStory-Assisted Analysis

## Status

**Completed exploratory CoreStory run. Strong candidate-qualification signal; not valid as a clean quantitative A/B benchmark.**

## Purpose

Repeat the broad CTS non-determinism investigation with CoreStory application intelligence available while retaining the same Synopsys non-determinism skills and the same user prompt used for TC-001A.

The intended experimental change was the addition of CoreStory MCP and a governing CoreStory qualification rule. The purpose was to determine whether broader application context changes which suspected non-determinism candidates survive deeper investigation.

## Test Configuration

- **Application:** Fusion Compiler CTS
- **CoreStory MCP:** Enabled
- **CoreStory qualification rule:** Enabled (`code-analysis-v2.mdc`)
- **Synopsys non-determinism skills:** Enabled and unmodified
- **Ground-truth TSan/Coverity findings:** Held out
- **Severity requested:** HIGH and MEDIUM

User-specific local paths, CoreStory project identifiers, conversation/session identifiers, and infrastructure details have been removed because they do not contribute to SME validation.

## Prompt

The prompt was intentionally unchanged from TC-001A and did not instruct the model to look for specific known defects or use CoreStory for a particular candidate:

```text
/nd-code-analyzer scan <CTS_WORKSPACE> for non-determinism, only HIGH and MEDIUM issues, and generate a shareable markdown report
```

## Final Result

After mechanical discovery and deeper source/application qualification, the CoreStory-assisted report promoted:

| Severity | Promoted findings |
|---|---:|
| HIGH | 0 |
| MEDIUM | 0 |

This result should **not** be interpreted as "CoreStory found no defects." The important observation was that application-level evidence changed the disposition of candidates that had previously been promoted or appeared suspicious during discovery.

## Qualification Summary

| Candidate | Earlier / suspected classification | TC-001B disposition | Primary qualification evidence |
|---|---|---|---|
| `ctoFlowClone.cc` pointer-set iteration | HIGH / real | **Dead / not in production build** | File absent from relevant production build; active implementation uses deterministic pointer comparator |
| `fmaxLpSolver::selectActiveVariableSubset` `std::random_device` | HIGH / real | **Dead / unused** | Only identified call site was commented out; no other live references found |
| `TimingCostFunction` parallel TNS fold | MEDIUM / real | **Configuration sensitivity** | Fixed range partitioning and thread-index fold for a fixed thread count |
| `ctoGrpLatCalc::calcGrpLatencyBatch` `hardware_concurrency` | MEDIUM / real | **False positive for result ND** | Worker writes were disjoint; grain selection did not demonstrate a changed arithmetic result |
| `msClustering` / tap `kMeansPPSeeding` | HIGH candidate | **Not equivalent-run ND** | Default-seeded Mersenne engine produced repeatable sequence for equivalent fresh runs |
| `runSccIteration` parallel reduction | MT candidate | **Neutralized for boolean QoR** | Associative boolean reduction; early-exit behavior did not change final boolean result |
| `unordered_set` used by offset/back-propagation paths | Static pattern candidate | **Membership-only** | Observed use was lookup/membership rather than order-sensitive iteration |

These are **experimental dispositions pending Synopsys SME validation**.

---

## Representative Qualification — `ctoFlowClone.cc`

### Original candidate

TC-001A promoted a HIGH candidate in:

**File:** `ctscto/ctoFlowClone.cc`  
**Function:** `ctoFlow::restructFlow()`  
**Approximate location:** line 1884

The suspicious construct used default pointer ordering:

```cpp
std::set<ndmTerm*> candidates;
std::set<ndmTerm*> lpCandidates;
// ... collect drivers ...
for (auto it = lpCandidates.begin(); it != lpCandidates.end(); ++it) {
  if (cloneBufferInverter(*it)) { ... }
  else if (bufShieldBufferInverter(*it)) { ... }
}
for (auto it = candidates.begin(); it != candidates.end(); ++it) {
  // ...
  if (countCands > (int)(10 * maxClockTree / 100)) break;
}
```

At the local-code level this is a credible non-determinism mechanism: pointer address ordering can vary, the iteration feeds mutating operations, and an early-break condition makes ordering potentially significant.

### Application qualification

The CoreStory-assisted investigation expanded beyond the local construct and reported:

1. `ctoFlowClone.cc` was **not included** in `ctscto/Master.make`.
2. The relevant production implementation was identified in `ctoRestruct.cc`.
3. The production path used `termSetType` rather than a default `std::set<ndmTerm*>`.
4. `termSetType` used `ndmObjPtrCmpType`, providing deterministic pointer ordering.
5. The production implementation was traced to a call from `ctscto.cc` under the applicable restructuring path.

The reported production shape was therefore materially different from the suspicious source construct:

```text
Suspicious source implementation
  ctoFlowClone.cc
  std::set<ndmTerm*>
          |
          X  not included in relevant production build

Production path
  ctscto.cc
      -> ctoRestruct.cc
      -> restructFlow(termSetType ...)
      -> termSetType uses ndmObjPtrCmpType
      -> deterministic pointer ordering
```

### Experimental disposition

**DEAD / NOT IN PRODUCTION BUILD** for the original `ctoFlowClone.cc` candidate.  
**SAFE-ADOPTER** for the corresponding investigated production implementation.

The significance of this example is that the suspected mechanism was plausible when viewed locally. The disposition changed only after build and application relationship evidence was incorporated.

### SME validation

- [ ] Confirm `ctoFlowClone.cc` is excluded from the relevant production build
- [ ] Confirm `ctoRestruct.cc` is the applicable production implementation
- [ ] Confirm the traced `ctscto.cc` call path is relevant
- [ ] Confirm `termSetType` uses `ndmObjPtrCmpType`
- [ ] Confirm comparator semantics provide deterministic ordering for this use
- [ ] Agree with experimental disposition
- [ ] Disagree with experimental disposition
- [ ] Additional investigation required

**SME notes:**

---

## Qualification — `fmaxLpSolver::selectActiveVariableSubset`

### Candidate

**File:** `fmaxLpSolver.cc`  
**Function:** `fmaxLpSolver::selectActiveVariableSubset`  
**Approximate location:** line 3892  
**Mechanism:** `std::random_device`

Entropy-seeded randomness on a live QoR path would be a strong non-determinism candidate.

### Application qualification

The investigation reported that the only identified caller was commented out around `fmaxLpSolver.cc:146–147` and that no other live references to the function were found.

### Experimental disposition

**DEAD / UNUSED**

The finding illustrates the distinction between identifying a nondeterministic mechanism in source and establishing that the mechanism participates in the executable application path.

### SME validation

- [ ] Confirm the identified call site is commented out
- [ ] Confirm no other production callers exist
- [ ] Agree with experimental disposition
- [ ] Disagree with experimental disposition
- [ ] Additional investigation required

**SME notes:**

---

## Qualification — Parallel TNS Fold

### Candidate

A parallel TNS reduction was investigated as a possible result-ordering issue.

### Application qualification

The run reported fixed range calculation and a thread-index-based fold. For a fixed thread count, the investigation concluded that equivalent runs use a stable partition/merge structure.

### Experimental disposition

**CONFIGURATION SENSITIVITY**, rather than confirmed equivalent-run non-determinism.

This distinction matters: behavior that can differ when execution configuration changes is not necessarily nondeterministic across equivalent runs with the same configuration.

### SME validation

- [ ] Confirm range partitioning behavior
- [ ] Confirm merge/fold ordering
- [ ] Confirm fixed-thread-count equivalent-run behavior
- [ ] Agree with experimental disposition
- [ ] Disagree with experimental disposition
- [ ] Additional investigation required

**SME notes:**

---

## Qualification — `ctoGrpLatCalc::calcGrpLatencyBatch`

### Candidate

Use of `hardware_concurrency()` influenced grain sizing and was investigated as a possible MEDIUM result-ND issue.

### Application qualification

The investigation reported that workers write to disjoint `grpLat[i]` locations. A different grain size could alter work distribution, but no mechanism was established by which that distribution changed the arithmetic result.

### Experimental disposition

**FALSE POSITIVE FOR RESULT NON-DETERMINISM**

### SME validation

- [ ] Confirm worker writes are disjoint
- [ ] Confirm grain sizing does not change result semantics
- [ ] Agree with experimental disposition
- [ ] Disagree with experimental disposition
- [ ] Additional investigation required

**SME notes:**

---

## Additional Qualification Examples

### `msClustering` / tap `kMeansPPSeeding`

The investigation found a default `boost::mt19937` engine. The experimental conclusion was that fresh objects use the same default seed and therefore the same random sequence across equivalent runs. This was retained as a determinism-hygiene consideration rather than promoted as a HIGH equivalent-run defect.

**SME validation:** Pending.

### `runSccIteration` parallel reduction

A parallel reduction involving `globalDone` was investigated. The result was classified as neutralized for boolean QoR because the reduction was associative and the observed early-exit behavior did not change the final boolean result.

**SME validation:** Pending.

### Membership-only unordered containers

Pointer-based unordered containers in the investigated offset/back-propagation paths were dismissed where the observed operations were membership lookup (`find`/`insert`) and no order-sensitive consumer was established.

**SME validation:** Pending.

## What TC-001B Demonstrated

The strongest directional signal was **candidate qualification**, particularly the ability to ask questions that require context beyond the suspicious source line:

```text
Is the code built?
        -> Is it reachable?
        -> Is the relevant runtime/configuration path active?
        -> Does the suspected mechanism propagate?
        -> Is it neutralized before an observable boundary?
        -> Can it affect an equivalent-run result?
```

The `ctoFlowClone.cc` example is particularly useful because the local source construct remains suspicious. The changed disposition came from establishing that the suspicious implementation was not the implementation used by the relevant production build and that the active implementation used deterministic ordering.

## Experimental Limitations

### Prior analysis artifacts were available

TC-001B encountered and reused ND artifacts generated earlier in the exploratory work. It therefore cannot be treated as a clean independent discovery run against TC-001A.

This does not invalidate the individual qualification evidence, but it prevents attributing differences in discovery coverage solely to CoreStory.

### Agent/model orchestration was not fully controlled

The execution environment exhibited autonomous routing/orchestration behavior that prevented authoritative model-specific token or cost attribution.

### Expected helper scripts were unavailable

The installed workflow did not contain the expected scanner/report helper scripts, so the agent used a fallback combination of repository search, source inspection, and CoreStory-assisted investigation.

## Interpretation

TC-001B supports a narrower and more defensible conclusion than a simple comparison of `7 findings` versus `0 findings`:

> **Application context materially changed the qualification of suspected non-determinism candidates by adding evidence about build inclusion, production reachability, implementation relationships, deterministic neutralization, and downstream behavior.**

Whether each resulting disposition is technically correct remains subject to Synopsys SME validation. The exploratory test also does not establish a precise token, runtime, cost, recall, or false-positive improvement percentage.

The customer-controlled A/B test was created to evaluate those questions under a more controlled environment.

# TC-001A — Baseline Control

## Status

**Completed exploratory baseline. Valid for directional analysis; not a final quantitative benchmark.**

## Purpose

Establish the behavior of the existing Synopsys AI-assisted non-determinism workflow against the CTS source without CoreStory application intelligence.

This run was intended to provide a baseline for comparison with the CoreStory-assisted exploratory run while keeping the source scope, discovery task, and installed Synopsys skills consistent.

## Test Configuration

- **Application:** Fusion Compiler CTS
- **CoreStory MCP:** Disabled
- **CoreStory governing rule:** Disabled
- **Synopsys non-determinism skills:** Enabled and unmodified
- **Ground-truth TSan/Coverity findings:** Held out
- **Severity requested:** HIGH and MEDIUM

The user-specific local workspace path has been removed from this package because it does not contribute to technical validation.

## Prompt

```text
/nd-code-analyzer scan <CTS_WORKSPACE> for non-determinism, only HIGH and MEDIUM issues, and generate a shareable markdown report
```

## Results

The run produced the following discovery funnel:

| Metric | Result |
|---|---:|
| Raw Stage-1 candidates | 4,535 hits across 817 files |
| HIGH findings promoted | 1 |
| MEDIUM findings promoted | 6 |
| Total promoted findings | 7 |
| Dismissed candidate buckets | 23 |
| Catalog patterns evaluated | 22 of 27 |

The promoted findings were concentrated in pointer-container ordering and equal-key/equal-delay tie-breaking behavior.

## Promoted Findings

| ID | Severity | Location | Suspected mechanism |
|---|---|---|---|
| H1 | HIGH | `ctscto/ctoFlowClone.cc:1884` | Default pointer ordering in `std::set<ndmTerm*>` influences mutating restructuring order |
| M1 | MEDIUM | `mscts/mstap/msTapSubtreeSyn.cc:285` | Distance-only sort allows equal-distance ties to influence repeater-anchor selection |
| M2 | MEDIUM | `mscts/mstap/msTapSubtreeSyn.cc:805` | Distance-only sort allows equal-coordinate ties to influence recursive cluster membership |
| M3 | MEDIUM | `ctscto/ctosc/ctoscLoadPartition.cc:136` | `min_element` has no deterministic final tie-break for equal-delay sinks |
| M4 | MEDIUM | `ctscto/ctosc/ctomt/ctomtReloc.cc:868` | `max_element` tie selects first load based on existing order |
| M5 | MEDIUM | `ctscto/ctosc/ctomt/ctomtReloc.cc:882` | `min_element` tie selects first load based on existing order |
| M6 | MEDIUM | `ctscto/ctoUtil.cc:4384` | Tied minimum delay selects first load and can influence gain filtering |

These are the **baseline run's classifications**. They are preserved here so that an SME can validate whether each candidate represents a real production nondeterminism defect.

## Representative HIGH Finding — H1

### Candidate

**File:** `ctscto/ctoFlowClone.cc`  
**Function:** `ctoFlow::restructFlow()`  
**Approximate location:** line 1884  
**Baseline classification:** HIGH / real

The baseline analysis identified two pointer-keyed sets using default pointer ordering and subsequent order-sensitive mutation:

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

### Why the baseline promoted it

The analysis reasoned that default ordering of pointer values can vary across equivalent executions. In this path, iteration drives calls that mutate netlist/timing state, and the non-LP loop also contains an early-exit quota. The baseline therefore concluded that iteration order could influence which transformations are attempted and promoted the candidate as HIGH.

### Baseline downstream reasoning

The reported path was:

```text
std::set<ndmTerm*> pointer order
        -> ctoFlow::restructFlow()
        -> cloneBufferInverter / bufShieldBufferInverter
        -> mutating transformation + early-break behavior
```

No deterministic neutralizer was identified by the baseline before the mutation point.

### SME validation

- [ ] Confirm the identified source construct
- [ ] Confirm this implementation participates in the relevant production build
- [ ] Confirm production reachability
- [ ] Confirm order can affect the mutating transformation
- [ ] Agree with baseline HIGH classification
- [ ] Disagree with baseline classification
- [ ] Additional investigation required

**SME notes:**

---

## MEDIUM Finding Detail

### M1 — Distance-only sort ties pick repeater anchor

**File:** `mscts/mstap/msTapSubtreeSyn.cc:285`

The baseline reported that `std::sort(termDistances)` relies on a distance-only comparison and that the odd-fanout path uses the first sorted load as an input to repeater placement. Equal-distance elements therefore lacked an explicit stable tie-break.

**SME validation:** Pending.

### M2 — Distance-only sort ties split recursive clusters

**File:** `mscts/mstap/msTapSubtreeSyn.cc:805`

The same comparison behavior was reported in a clustering path where the sorted sequence is divided into `loadTerms1` and `loadTerms2` before recursive clustering. The baseline concluded that equal-coordinate ties could alter cluster membership.

**SME validation:** Pending.

### M3 — SP sink `min_element` tie

**File:** `ctscto/ctosc/ctoscLoadPartition.cc:136`

The comparator was reported to return no deterministic final ordering when early/late delay values were equal. The selected sink influences `_spSinkPos` and subsequent partition behavior.

**SME validation:** Pending.

### M4 / M5 — Gskew relocation min/max delay ties

**File:** `ctscto/ctosc/ctomt/ctomtReloc.cc:868, 882`

The baseline reported that tied delay extrema could select the first element according to the existing input order and that the selected load participates in relocation-candidate generation.

**SME validation:** Pending.

### M6 — SP-filter minimum-delay tie

**File:** `ctscto/ctoUtil.cc:4384`

The baseline reported that tied minimum delay values could select the first load and that the resulting index participates in gain filtering and new driver-location processing.

**SME validation:** Pending.

## Examples of Candidates Dismissed by the Baseline

The analysis also rejected many initial pattern matches after deeper inspection. Reported categories included:

- latent-only concurrency patterns;
- MT paths without a demonstrated shared-worker caller;
- index-disjoint writes where result nondeterminism was not demonstrated;
- behavior neutralized by deterministic processing before an observable sink;
- existing deterministic pointer-comparator adopters;
- test/debug-only behavior not shown to affect production QoR.

This filtering is important because the test was not intended to equate a static pattern match with a proven defect.

## Experimental Limitations

This run exposed execution variability in the AI test harness. The agent autonomously decomposed portions of the analysis into child sessions despite visible controls intended to limit that behavior. Model attribution across the generated execution was also not sufficiently controlled for a model-specific economic comparison.

The installed workflow also lacked expected scanner/report helper scripts, causing the agent to construct a fallback Stage-1 search workflow.

These limitations do **not** erase the individual source findings, but they mean runtime, token usage, and the final finding count should be treated as exploratory evidence rather than a controlled benchmark.

## Interpretation

TC-001A established a useful baseline candidate set and demonstrated the scale of the qualification problem: thousands of initial pattern matches were narrowed to seven promoted HIGH/MEDIUM findings.

The next exploratory test, TC-001B, retained the same broad discovery task while adding CoreStory application intelligence. The important comparison is therefore not only whether the number of promoted findings changed, but **why particular candidates survived or failed deeper application-level qualification**.

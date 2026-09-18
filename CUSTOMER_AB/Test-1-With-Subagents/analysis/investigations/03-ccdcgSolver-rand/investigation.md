I now have sufficient evidence to complete the investigation checkpoint. The CG solve uses a serial conjugate-gradient library (`wn_conj_funcgrad_method`) with callbacks that contain no `rand()`; RNG use is confined to the single sequential loop in `seedAndPruneCands()`.

---

# Investigation Checkpoint — Non-Determinism Candidate in `ccdcgSolver.cc`

**Playbook:** `agentic-bug-resolution` · **CoreStory scope:** project **10 (`cts-code`)** only · No source modified.

## Problem Summary
The reported candidate is `srand()/rand()` at `ccd/ctsccd/cgbased/ccdcgSolver.cc:501–505`, hypothesized as a non-determinism (ND) source via process-global PRNG state. Treated as hypothesis. The central finding is that the seed is **hard-coded (`srand(100)`)** and is **reset immediately before** the only `rand()` loop, which makes the RNG a *deterministic function of candidate index* rather than a classic ND source. The hypothesis as stated is **not supported** by the direct evidence; a narrow residual concern is re-characterized below.

## The candidate code (direct source evidence)

```494:510:ccd/ctsccd/cgbased/ccdcgSolver.cc
ccdcgSolver:: seedAndPruneCands()
{
  int numVars = _candidates.size();
  std::vector<float> randSeed( numVars );
  srand( 100 );
  for( int i=0; i < numVars; ++i ) {
    float candSeed =  0.0;
    /* coverity[dont_call] */
    int r = rand();
    float rSeed = ((float)((r % 50001) + 50000))/1000000.0;
    randSeed[i] = rSeed;
    _vals[i] = (candSeed != -1.0) ? candSeed : (_args._seed - rSeed);
```

Consumption of the RNG-derived values (the only live use):

```545:551:ccd/ctsccd/cgbased/ccdcgSolver.cc
      if ( !candSatisfied ) {
        cand->setCannotZero();
        if ( _vals[index] < 0.5 )
          oneSeedCount++;
        _vals[index] = (float) 1.0 - randSeed[index];
```

## Findings against the 13 required determinations

1. **In production build?** **Yes (direct).** `ccdcgSolver.cc` is listed in `ccd/ctsccd/cgbased/Master.make` (`MODULE = cgbased`). Not a test module.

2. **Reachable from production?** **Yes (direct + CoreStory).** Chain: `ccdcgFlow::runCore` → `runBatches` → `optimizeDriver` → `runCG` (`ccdcgFlow.cc:333`) constructs `ccdcgSolver` and calls `solve()` → `seedAndPruneCands()` (`ccdcgSolver.cc:363`). CoreStory (proj 10) describes `runCore` as the "CG-based CCD … optimization" phase and the `ccdcgSolver` chunk as the "seeds and prunes candidates" heuristic. Gated by `runCore`: design must be `ROUTED` and timing not already good enough.

3. **How/where seeded?** **Direct.** `srand(100)` — a **fixed literal seed** at line 501, immediately before the loop that consumes `rand()`.

4. **Can the seed vary between equivalent executions?** **No (direct).** The seed is a constant (`100`). It is not derived from time, PID, address, thread ID, or config. This is the single most important fact: it negates the reported mechanism ("if the seed … can vary").

5. **Do other production consumers share/modify the same global RNG before/during this path?** **No relevant production consumer (direct).** Repo-wide, the only other `srand/rand` sites are: `skewgrp/ctsSkewgroup.cc`, `skewgrp/ctsDStest.cc` (standalone `ctsDSNS::main`; **`skewgrp/Master.make` has empty `CPPFILES`** → not built), `ctsutil/test/ctsGfxDrawTest.cc` (test dir), `ctsui/ctsuiscRandomTest.cc` (**not** in `ctsui/Master.make`), and `ctsui/ctsuiCtoRandomTest.cc` (built, but a self-contained random **test command** class that itself calls `srand(0)`/`srand(getIdLong())`, run as an explicit user test, not in the CTS opto flow). Critically, even if any ran earlier, `srand(100)` **resets** global state before the loop, so prior state is irrelevant.

6. **Can call count / ordering vary?** **Call count/order within the loop: deterministic (direct).** `rand()` is called exactly `numVars` times in strict index order. Because `srand(100)` fixes the sequence, the *i*-th draw is always identical; `randSeed[i]` depends only on index `i`, independent of `numVars`. The one real dependency is **which candidate receives index `i`** — set by upstream insertion order in `ccdptProblemGenerator::populateCgData` (`addCand`, line 2301). That is an *upstream ordering* property, not an RNG property.

7. **Concurrent with any other `srand/rand` consumer?** **No (direct + CoreStory).** `runCG`/`solve`/`seedAndPruneCands` execute sequentially on the main thread. The multithreaded region is `_xformSuite->runAccurate()` inside `optimizeDriver` (write locks suspended for MT subgraph evaluation), which **completes before** `runCG`. CoreStory corroborates: MT is for "accurate subgraph evaluation"/"multithreaded read access," and the CG solve follows. The CG numerical core (`wn_conj_funcgrad_method` with `ccdGradFuncCb`/`ccdTerminateCb`) contains no `rand()`. No parallel solver instances (one per `runCG`, sequential).

8. **How are values consumed?** **Direct.** `candSeed` is hard-coded `0.0`, so line 509 always sets `_vals[i]=0.0` (the `_args._seed - rSeed` branch is dead). `rSeed ∈ [0.05, ~0.100001]` is stored and later applied only to "one-seeded" (cannot-zero) candidates as `_vals[index] = 1.0 - randSeed[index]` (≈0.90–0.95) — a small deterministic perturbation of the CG **initial guess**.

9. **Is the difference neutralized downstream?** **Partially (direct + inference).** Sorting is deterministic (`std::sort` with `compareFunc`, which uses `index()` as final tiebreaker). Final selection is a threshold (`_vals[i] > _args._candSelThresh`). A perturbation could only alter output if it steered CG to a different local optimum flipping a near-threshold candidate. Since the perturbation is a fixed function of index, it is reproducible across equivalent runs and does **not** by itself inject variation.

10. **Credible path from RNG-state variation to observable output?** **Not from the RNG itself (inference).** The RNG cannot vary between equivalent runs (fixed seed, no concurrency, no shared state). A path to observable output exists *only if upstream candidate ordering/index assignment varies* — in which case the same fixed perturbation lands on different candidates and could change convergence/selection. That makes this code an *amplifier/propagator* of any pre-existing upstream ordering ND, not an independent ND source.

11. **Required runtime/config conditions.** Design `ROUTED`; CG-CCD not auto-skipped (timing above threshold); a batch with candidates reaching the "cannot-zero"/one-seed branch; and, for any observable effect, at least one candidate whose converged value sits near `_candSelThresh`.

12. **Blast radius if real (as an amplifier).** Scope-limited to CG-CCD TNS/timing optimization candidate selection → potentially different buffering/sizing/reparenting choices → downstream topology/QoR/timing deltas. It would not, on its own, produce run-to-run variation for identical inputs; impact requires an upstream ordering non-determinism to exist.

13. **Unresolved / needs SME or runtime validation.** (a) Whether `populateCgData`/`ccdptProblemGenerator` candidate insertion order is itself fully deterministic (pointer-address or hash-set iteration order would be the real ND source, which this code would then propagate). (b) Whether any near-threshold sensitivity is realistic in practice. (c) SME intent confirmation that `srand(100)` is a deliberate "deterministically random" seeding choice (the `/* coverity[dont_call] */` suppression indicates awareness; the sibling test uses the same "deterministically random" idiom).

## Evidence classification
- **Direct source evidence:** fixed `srand(100)`; single sequential `rand()` loop; dead `candSeed` branch; consumption at line 549; Master.make build inclusion/exclusion; sequential `runBatches`→`runCG` with MT confined to `runAccurate`; no `rand` in CG callbacks; other consumers are unbuilt or separate test commands.
- **CoreStory application evidence (proj 10):** `ccdcgSolver` = candidate seed/prune heuristic; `ccdcgFlow::runCore` = CG-CCD optimization phase; write-lock suspension is for multithreaded subgraph read/eval, with CG solve following.
- **Reasoned inference:** RNG is a deterministic function of index; can only amplify upstream ordering ND; near-threshold flip is the theoretical output path.
- **Unresolved questions:** upstream candidate-ordering determinism; near-threshold sensitivity; SME intent.

## Assessment
The reported defect **as framed (srand/rand as an independent ND source) is not supported**. The fixed seed, immediate re-seed, single-threaded execution, and absence of concurrent production RNG consumers make the PRNG output reproducible for equivalent inputs. The only credible ND contribution is **conditional and indirect**: if upstream candidate index ordering is non-deterministic, this fixed per-index perturbation would be applied to different candidates and could propagate that variation into selection near the threshold. Investigation should pivot upstream to `ccdptProblemGenerator` ordering rather than the RNG call.

## Validation plan (no code changes)
1. **Confirm reproducibility of the RNG output:** in a debugger/instrumented run, dump `randSeed[]` and the `rand()` sequence for two identical-input runs — expect bit-identical sequences (validates fixed-seed determinism).
2. **Test the real hypothesis (upstream ordering):** log the candidate identity→index mapping from `populateCgData` across two identical runs; check for reordering (pointer-sorted containers, unordered_set/map iteration).
3. **Sensitivity probe:** count candidates whose converged `_vals[i]` lie within a small epsilon of `_candSelThresh`; if none, output is insensitive to the perturbation regardless.
4. **Concurrency assertion:** confirm (assert/trace) that `seedAndPruneCands` runs only on the main thread and that no `runAccurate` worker outlives into `runCG`.
5. **SME confirmation:** verify with the CCD owner (Master.make `OWNERS`) that `srand(100)` is intentional "deterministically random" seeding and whether upstream ordering is contractually deterministic.

**Classification:** Not ready for a code fix on the reported line. Recommend redirecting the ND investigation to upstream candidate ordering in `ccdptProblemGenerator`; a change to `ccdcgSolver.cc` would be unjustified without evidence from steps 1–2 above.

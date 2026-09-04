# Multi-threaded nondeterminism analysis
_Exported on 9/4/2026 at 11:28:19 CDT from Cursor (3.18.25)_

---

**User**

Investigate the repository for multi-threaded nondeterminism caused by commit-order dependence or first-writer/first-finder-wins behavior.

Use the prove-nd-mt skill and follow the CoreStory code-analysis rule.

Start with CoreStory. Before broad local repository searching, identify the strongest application-level path you can support that includes:
1. a parallel dispatch or concurrent producer set,
2. two or more producers that can generate competing valid results,
3. a shared destination, commit point, selection site, or winner field,
4. a commit/selection order that can vary across equivalent runs, and
5. a downstream consumer whose observable behavior can depend on which result wins.

For any candidate, do not classify it as Real until you establish:
1. the competing producers actually execute concurrently,
2. their completion or commit order can vary across equivalent runs,
3. the shared destination preserves or exposes that ordering choice,
4. the selected value reaches an observable application result, and
5. no complete deterministic arbitration, stable tie-break, canonicalization, re-sort, or post-join recomputation neutralizes the ordering before that consumer.

Use local source inspection to validate the strongest CoreStory-supplied path. Avoid broad product-wide grep unless CoreStory cannot establish a candidate path; if you must broaden the search, make that explicit.

Return only the strongest supported candidate, or state that the available evidence is insufficient.

---

**Cursor**

I'll investigate commit-order / first-writer-wins nondeterminism using the prove-nd-mt skill and CoreStory first. Reading the skill, then querying CoreStory for the strongest application-level path.

Next I'll load the base prove-nd skill and CoreStory tool schemas, then query for commit-order / first-writer-wins candidates.

Listing CoreStory projects and opening a conversation aimed at commit-order / first-writer-wins paths.

Asking CoreStory for the strongest full causal path (parallel producers → shared winner → observable consumer).

CoreStory points at `ctomtGlsParallelBufPlans` / `_winner`. Validating concurrency, selection order, and whether cost-based arbitration neutralizes it.

CoreStory says `_winner` is post-join and may be overridden by `selectBestPerDriver`. Inspecting that path locally and hunting for true concurrent first-writer sites.

Confirming `_winner` is stats-only and `selectBestPerDriver` runs first. Digging into CoreStory's remaining first-finder candidates and the parallel eval path.

Doing one narrow follow-up on budget/early-exit and concurrent shared-result appends, then validating any hit locally.

**Verdict: available evidence is insufficient** for a Real multi-threaded commit-order / first-writer-wins finding.

### Strongest CoreStory path examined (neutralized)
`ctomtGlsParallelBufPlans` / `driverInfo::_winner` looked like the best fit, but local validation rejects it as MT first-writer ND:

1. **Parallel producers exist** — Phase 2 evaluates expanded per-plan problems via `_xformSuite->runAccurate(evalProblems)` in `ctomtGlsLevelFlow.cc` / `ctomtGlsFlow.cc`.
2. **No concurrent winner write** — `aggregateDriverInfo` is a post-join serial scan; workers do not race `_winner`.
3. **Deterministic arbitration before consolidate** — `selectBestPerDriver` runs first and picks by `costVector::compare`; losers are cleared with `setFoundSolution(false)`.
4. **`_winner` is not the commit authority** — it is only a stats sink in `disposeEvalProblems`; the header states consolidate runs *after* `selectBestPerDriver`.
5. **Container order is construction order** — `expandGlsBufferingProblems` appends plans in fixed loops; no evidence that completion order reshuffles `evalProblems`.

### Other CoreStory leads
Search drivers (`ctsSearchDlyDriver`, `ctsSearchClockTreeDriver`), `ctsXformProblems`, LP wrappers, budget/early-exit, and concurrent append-then-commit: CoreStory could not establish concurrent producers racing a shared winner that survives to an observable result without post-join arbitration. No broader product-wide grep was done beyond those CoreStory-named sites.

**Missing for a Real claim:** a live path where concurrent workers update the same shared winner/found field (or append in completion order), that ordering can vary across equivalent runs, and the chosen value reaches design/QoR output without a complete deterministic re-selection.


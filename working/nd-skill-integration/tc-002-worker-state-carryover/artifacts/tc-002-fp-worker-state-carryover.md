# Multi-threaded nondeterminism analysis
_Exported on 9/4/2026 at 10:49:01 CDT from Cursor (3.18.25)_

---

**User**

Investigate the repository for multi-threaded nondeterminism caused by worker-state carryover across reused worker objects.

Use the prove-nd-mt skill and follow the CoreStory code-analysis rule.

Start with CoreStory to identify long-lived worker objects, thread-server or worker-pool reuse, work-item assignment behavior, mutable per-worker state, lifecycle entry/exit methods, accessors, and downstream consumers.

For any candidate, do not classify it as Real until you establish:
1. the worker object is reused across multiple work items,
2. work-item-to-worker binding can vary across equivalent runs,
3. a relevant member can retain state from a prior work item,
4. neither the entry side nor exit side unconditionally restores that state before it is consumed, and
5. the carried value can affect an observable application result.

Inspect both sides of the work-item boundary. Do not assume that a method named reset, clear, flush, or similar fully neutralizes the state; verify what it actually changes and whether all relevant members/accessors are covered.

Return only the strongest supported candidate, or state that the available evidence is insufficient.

---

**Cursor**

I'll follow the prove-nd-mt skill and CoreStory workflow: first read the skill, then query CoreStory for long-lived workers and reuse/carryover patterns.

Next I'll pull CoreStory tool schemas and start an application-level query for worker reuse and state carryover.

CoreStory surfaced several candidates; I'll narrow to true pooled-worker carryover and validate against source.

Searching the codebase for the classic worker patterns from the skill, and inspecting the strongest CoreStory leads in source.

Inspecting source for true per-thread worker objects versus per-job state.

Validating `ctoscLoadPartition` against the five Real criteria—CoreStory's claim needs source proof.

**Verdict: evidence is insufficient for a Real worker-state carryover finding.**

CoreStory (project `cts-code`, conversation on worker carryover) plus source inspection did not establish all five Real criteria for any candidate.

### What was checked
- **Pool / dispatch:** `ctsMtMgr` pre-creates threads and assigns work via `queueWork` / `nqTaskManagerHybrid` (`ctsutil/ctsMtMgr.cc`) — dynamic binding is real.
- **Near-miss per-thread state:** `fmaxcgSolverImpl` `threadSpecificQGradMap::_grads` accumulates under MT, but `consolidateTimingGradient` zeroes each updated slot after merge (`ccd/ctsccd/fmax/fmaxcgSolverImpl.cc`) — **Neutralized**.
- **Dismissed “partition worker”:** `ctoscLoadPartition` is stack-local per call in `ctomtBuffer.cc`, not a pooled worker — fails reuse / binding criteria.
- **Other leads** (`ctoLocalSkewMgr` per-thread holders, lazy-TNS job caches, `ctoscTimerCache`, delay/ICDB engines): either cleared/destroyed after merge, are job-local rather than worker-local, or lack a proven stale read into an observable result.
- Classic skill patterns (`startProblem` / `flushMap` / maze thread-server) are not present as a matching defect surface in this tree.

### Strongest near-miss
**`ctsMtMgr` / `ctsMtThreads` / `ctsMtTask`** — proves (1) long-lived workers and (2) dynamic binding, but **fails (3)+(4)+(5) together**: no concrete unreset worker member was shown to be written by work item A, left unrestored on entry/exit, and later consumed into an observable application result for work item B.

**Classification:** Unresolved / insufficient for `Worker-carryover` → Real.  
**Next validation if pursued:** instrument `(worker id, work-item id, candidate member)` across two identical runs on the `ctsMtMgr` path, or audit `nqThreadHandleHybrid` / `mtmsThreadDataHolder` payloads beyond what is in-repo.


Use the agentic-bug-resolution playbook to investigate a reported
non-determinism defect in Fusion Compiler CTS.

CoreStory scope constraint:

Use CoreStory project ID 10 (workspace: cts-code) for all CoreStory
application-context queries in this investigation.

Do not use cts-code2 or any other CoreStory project as evidence.

Treat the reported defect as a hypothesis, not as a confirmed finding.

Reported candidate:

File:
ccd/ctsccd/cgbased/ccdcgSolver.cc

Approximate location:
501

Reported mechanism:

The code uses srand()/rand() while constructing or processing solver
state. Use of process-global pseudo-random state can be a source of
non-determinism if the seed, number of calls, call ordering, concurrency,
or other consumers of the same RNG state can vary between otherwise
equivalent executions.

Investigate this candidate independently.

Determine:

1. Whether the affected source is part of the relevant production build.
2. Whether this code is reachable from production CTS execution paths.
3. How and where the random-number generator is seeded.
4. Whether the seed can vary between otherwise equivalent executions.
5. Whether other production code shares or modifies the same global RNG
   state before or during this execution path.
6. Whether call count or call ordering can vary because of iteration
   order, concurrency, configuration, or input traversal.
7. Whether the candidate executes concurrently with any other srand()
   or rand() consumer.
8. How the generated values are consumed by the solver.
9. Whether subsequent sorting, canonicalization, convergence behavior,
   fixed initialization, or another mechanism neutralizes differences.
10. Whether a credible path exists from RNG-state variation to
    observable CTS output, topology, timing, QoR, or another
    externally visible result.
11. What runtime/configuration conditions are required for the
    suspected behavior.
12. The likely blast radius if the defect is real.
13. What evidence remains unresolved and requires SME or runtime
    validation.

Trace the relevant execution path from upstream production entry points
through RNG initialization and consumption into downstream solver
behavior.

Search for other relevant srand()/rand() consumers and establish whether
they can actually participate in the same production execution path.
Do not classify a consumer as relevant solely because it exists in the
repository.

Clearly distinguish:

- direct source evidence;
- CoreStory application evidence;
- reasoned inference;
- unresolved questions.

Do not use previous generated ND reports, benchmark comparison reports,
prior AI conclusions, or known defect lists as evidence.

Do not assume the reported defect is correct.

Do not modify source code.

Stop at the investigation checkpoint and provide an evidence-based
assessment and validation plan.

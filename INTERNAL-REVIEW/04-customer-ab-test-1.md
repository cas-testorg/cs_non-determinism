# 04. Customer A/B Test 1

## Test design

Test 1 compared two end-to-end workflows on the same CTS source snapshot:

- **Without MCP:** existing Synopsys ND workflow.
- **With MCP:** CoreStory-assisted workflow.

Because each arm performed its own discovery and qualification, Test 1 did not isolate application qualification from discovery. Model/subagent execution also formed part of the end-to-end workflow.

## Initial customer source review

| Measure | Without MCP | With MCP |
| --- | ---: | ---: |
| Promoted findings | 19 | 6 |
| Source-confirmed unique ND issues found | 8 | 4 |
| Coverage against initial 9-issue source-reviewed union | 89% | 44% |
| Promoted rows surviving as unique ND | 8/19 | 4/6 |

Across both arms, the comparison normalized 22 unique promoted rows. It classified 9 as source-confirmed current ND, 1 as a duplicate root cause, 10 as not current ND, and 2 as unresolved.

**Runtime reproduced: 0.**

The 9-issue union is therefore a source-reviewed comparison set, not runtime ground truth or final SME adjudication.

## What the initial result showed

On the customer's initial source review, the existing workflow demonstrated broader discovery coverage.

The With-MCP workflow produced a shorter promoted list, but shorter did not automatically mean higher quality. Two of the six CoreStory-assisted promoted findings did not survive the later source review.

At the same time, the CoreStory-assisted workflow uniquely surfaced msDrivers.cc:711, and its dismissal of the fixed-seed RNG candidate in ccdcgSolver.cc was supported by the source comparison.

## Four focused disagreement investigations

### soSolverUpdater.cc:2100

Without MCP promoted it as a TBB/shared-map data race. With MCP did not report it. The customer comparison classified it as real.

The focused investigation found production build/reachability, but also prepopulated map keys, single-threaded initialization, scenario partitioning, separate setup/hold loops, downstream consumption after the parallel join, and no demonstrated concurrent structural mutation.

**Current interpretation:** adjudication disagreement requiring SME/runtime validation, not a clean established CoreStory recall miss.

### msDrivers.cc:711

CoreStory-assisted only.

The focused investigation found raw-pointer set iteration, last-wins scalar return behavior, most callers neutralizing the scalar, and three MLPH/auto-tap callers preserving it with a credible path into clock/sink selection.

**Current interpretation:** source-substantiated latent ND, pending runtime confirmation of trigger conditions.

### ccdcgSolver.cc:501

Without MCP promoted global rand usage. With MCP dismissed it.

The focused investigation found a fixed literal seed, immediate reseed, sequential consumption, and no relevant concurrent production RNG consumer.

**Current interpretation:** reported RNG mechanism not substantiated. The CoreStory-assisted dismissal is supported for that mechanism.

### msuiGetPowerTaps.cc

With MCP promoted pointer-address-driven iteration ND. The customer source review later rejected it.

The suspicious structure exists, but the load-bearing dosUnorderedSet/hash implementation and downstream collection conversion implementation were unavailable.

**Current interpretation:** unsubstantiated on current evidence. The correct evidence-gated result should have been UNRESOLVED rather than a promoted real defect.

## What Test 1 supports

1. The existing Synopsys workflow was stronger at broad discovery against the initial source-reviewed union.
2. Promoted-finding count is not equivalent to validated-defect recall.
3. Application-level tracing can materially change candidate disposition.
4. CoreStory context does not protect against incorrect source inference when load-bearing implementation evidence is missing.
5. The A/B compared two end-to-end workflows and therefore cannot attribute every difference specifically to MCP.

The strongest follow-on hypothesis from Test 1 was to separate discovery from application qualification and evaluate the latter on a frozen candidate set.

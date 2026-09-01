# 5. Unstable Iteration and Traversal

Search for iteration or traversal whose visit order may vary and where that order could affect application state, decisions, calculations, serialization, or output.

Include:

- unordered containers
- hash-table traversal
- graph or work-list traversal whose ordering is not fixed
- iteration derived from insertion history
- traversal over dynamically assembled collections
- opportunistic traversal or early termination
- order-sensitive consumers of otherwise unordered data

## Concrete Exemplar

Use the following source pattern as a **concrete exemplar, not as a known defect**.

**File:** `ctssch/ctsPowerDrivenGateRelocator.cc`  
**Symbol:** batch commit path in `ctsPowerDrivenGateRelocator`

The source copies values from an unordered container and explicitly sorts them before downstream processing:

```cpp
// drivers must be sorted for deterministic iteration
std::vector<ndmInst *> allDrivers;
for (auto iter = _hashTblDrivers.begin(); iter != _hashTblDrivers.end(); ++iter) {
  allDrivers.push_back(iter->second);
}
std::sort(allDrivers.begin(), allDrivers.end(), ndmObjPtrCmpType());
for (auto iter = allDrivers.begin(); iter != allDrivers.end(); ++iter) {
  // downstream processing
}
```

This example demonstrates a potentially unstable traversal source and an explicit determinism-restoring sort.

The important investigation question is not merely whether unordered iteration occurs. It is whether the traversal order reaches an order-sensitive consumer before a stable ordering, normalization, or commutative operation removes the variability.

Use this exemplar to identify semantically equivalent patterns elsewhere in the application.

## Investigation Requirements

For each candidate:

1. Identify the container, graph, queue, work list, or traversal source whose order may vary.
2. Identify what can change that order, such as insertion history, hashing, rehashing, platform/library behavior, scheduling, or dynamic graph construction.
3. Identify the downstream consumer of the traversal order.
4. Determine whether downstream logic is order-sensitive, including:
   - first/last winner selection
   - incremental mutation
   - early exit
   - floating-point accumulation
   - tie breaking
   - serialization or report ordering
   - traversal-dependent heuristics
5. Identify stabilizing mechanisms such as sorting, canonical IDs, deterministic queues, stable insertion, commutative aggregation, or final normalization.
6. Trace the causal chain where supported:

   **variable traversal order**  
   → **order-sensitive consumer**  
   → **different downstream state, decision, or calculation**  
   → **observable application result**

7. Classify each candidate as:
   - confirmed unstable-order application nondeterminism;
   - plausible order sensitivity requiring evidence that order varies;
   - unstable traversal with effective determinism restoration;
   - order variation limited to diagnostics or presentation;
   - insufficient evidence.

Do not report a finding solely because an unordered container or non-stable traversal exists.

## Evidence Requirements

For each elevated candidate provide:

- file and symbol
- traversal source
- source of possible order variation
- downstream consumer
- why the consumer is or is not order-sensitive
- sorting, canonicalization, or mitigation
- relevant application execution path
- downstream application impact
- whether equivalent-run nondeterminism is established
- confidence
- missing evidence required for confirmation

Prefer a smaller number of well-supported findings over a larger number of speculative candidates.

For this test, do not use previously generated nondeterminism analysis documents, prior analysis artifacts, or prior investigation results.

Perform a new investigation using current CoreStory application intelligence and targeted source inspection.

# 4. Pointer-Dependent Ordering

Search for cases where pointer values, object addresses, or address-derived values influence ordering, hashing, traversal, selection, serialization, or downstream application behavior.

Include:

- `std::set<T*>` or `std::map<T*, ...>` using default pointer ordering
- pointer values used as hash keys where iteration order matters
- pointer-derived tie breakers
- sorting or comparison by object address
- address-based identifiers that affect output or decisions
- patterns similar to Coverity `POINTER_NONDETERMINISM`

## Relevant Defect Patterns

This investigation includes source patterns associated with:

- Coverity `POINTER_NONDETERMINISM`

Treat this name as an investigation pattern, not as evidence that a corresponding Coverity defect exists. Establish the address variation, order-sensitive consumer, and observable application impact independently.

## Concrete Exemplar

Use the following source pattern as a **concrete exemplar, not as a known defect**.

**File:** `mscts/msmesh/msIncrMerger.cc`  
**Symbol:** `msIncrMerger::mergeDriverNodes`

The implementation intentionally uses pointer comparison for set membership, then restores deterministic downstream ordering by sorting on a stable node comparator:

```cpp
std::set<msTreeNode *> mergedNodeSet;
std::set<msTreeNode *> outputNodeSet;

// ...
outputNodes.insert(outputNodes.end(), outputNodeSet.begin(), outputNodeSet.end());

// Sort output by node ID for determinism, since outputNodeSet uses pointer ordering
std::sort(outputNodes.begin(), outputNodes.end(), msTreeNodeCompare());
```

This example demonstrates both the address-dependent construct and a determinism-restoring mitigation.

The important investigation question is not merely whether pointers are used as keys. It is whether address-dependent ordering can reach an order-sensitive operation before a stable ordering, normalization, or commutative operation removes the variability.

Use this exemplar to identify semantically equivalent patterns elsewhere in the application.

## Investigation Requirements

For each candidate:

1. Identify the pointer-address-dependent container, comparator, hash, sort, or tie breaker.
2. Identify what could cause pointer values or allocation addresses to differ across equivalent executions.
3. Trace iteration, traversal, merge, selection, serialization, calculation, or decision logic that consumes the resulting order.
4. Determine whether downstream processing is order-sensitive.
5. Identify determinism-restoring mechanisms such as:
   - stable ID sorting
   - canonicalization
   - explicit stable comparator
   - commutative aggregation
   - order-independent set semantics
   - normalization before output or decision making
6. Trace the causal chain where supported:

   **address variation**  
   → **pointer-dependent order/hash/traversal**  
   → **order-sensitive downstream operation**  
   → **different state, calculation, selection, or output**  
   → **observable application result**

7. Classify each candidate as:
   - confirmed pointer-dependent nondeterministic application behavior;
   - plausible address-dependent behavior requiring additional evidence;
   - address-dependent construct with effective determinism restoration;
   - insufficient evidence.

Do not report a finding solely because a pointer is stored in `std::set`, `std::map`, or an unordered container. Establish that the resulting order can affect observable behavior.

## Evidence Requirements

For each elevated candidate provide:

- file and symbol
- pointer-dependent construct
- source of possible address variation
- iteration/traversal/selection consumer
- whether the consumer is order-sensitive
- stable sorting, normalization, or other mitigation
- relevant application execution path
- downstream application impact
- whether equivalent-run nondeterminism is established
- confidence
- missing evidence required for confirmation

Prefer a smaller number of well-supported findings over a larger number of speculative candidates.

For this test, do not use previously generated nondeterminism analysis documents, prior analysis artifacts, or prior investigation results.

Perform a new investigation using current CoreStory application intelligence and targeted source inspection.

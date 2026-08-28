# 3. Object Lifetime and Use-After-Free

Search for object-lifetime interactions where an object may be destroyed, released, invalidated, replaced, or reused while pointers, references, callbacks, tasks, containers, or other consumers may still retain access to it.

Include:

- heap use-after-free risks
- raw pointers that may outlive their owner
- objects deleted while asynchronous or parallel work may still reference them
- callbacks or queued jobs capturing object pointers
- containers that retain stale pointers after destruction
- singleton or cache teardown while dependent objects remain active
- ownership transfers with unclear lifetime guarantees
- manual reference counting
- teardown ordering across threads or tasks
- races between destruction and access

## Relevant Defect Patterns

This investigation includes source patterns associated with:

- ThreadSanitizer `HEAP USE AFTER FREE`

Treat this name as an investigation pattern, not as evidence that a corresponding ThreadSanitizer defect exists. Establish the ownership, destruction, stale-access path, and application impact independently.

## Concrete Exemplar

Use the following source pattern as a **concrete exemplar, not as a known defect**.

**File:** `mscts/mscore/msTreeNode.cc`  
**Symbol:** `msTreeNode::changeTreeRecursive`

The implementation tracks whether `oldTree` is actually present before using the recorded index:

```cpp
bool treeFound = false;
bool oldTreeFound = false;
unsigned oldTreeIdx = 0;
unsigned idx = 0;
for (msTree* tree : _trees) {
  // ...
  if (tree == oldTree) {
    oldTreeFound = true;
    oldTreeIdx = idx;
  }
  ++idx;
}

if (!oldTreeFound && !treeFound) {
  return;
}

// ...
_trees[oldTreeIdx] = newTree;
```

The surrounding source documents the failure mode this guard prevents: in a cascaded tap structure, an `oldTree` may never have been registered in `_trees`; using the default index could overwrite unrelated tree membership and later contribute to use-after-free during cleanup.

This example demonstrates that lifetime analysis must establish the actual ownership and invalidation sequence, not merely identify raw pointers or manual object management.

Use this exemplar to identify semantically equivalent lifetime patterns elsewhere in the application.

## Investigation Requirements

For each candidate:

1. Identify the allocated or owned object and the code responsible for its lifetime.
2. Trace creation, publication, sharing, ownership transfer, invalidation, and destruction.
3. Identify pointers, references, callbacks, tasks, jobs, caches, containers, or singleton state that can retain access.
4. Identify thread or task entry points that may overlap with destruction or invalidation.
5. Describe the exact sequence required for a stale or freed reference to be consumed.
6. Identify ownership, joining, synchronization, reference counting, container cleanup, guard checks, or lifecycle ordering that prevents the unsafe sequence.
7. Trace the causal chain where supported:

   **object creation/ownership**  
   → **reference retained or published**  
   → **object destruction/invalidation**  
   → **reachable stale access**  
   → **observable application impact**

8. Classify each candidate as:
   - confirmed unsafe lifetime path;
   - plausible but runtime-dependent;
   - effectively protected by ownership/lifecycle ordering;
   - insufficient evidence.

9. Distinguish an established lifetime defect from an established nondeterministic manifestation. If nondeterminism is claimed, identify what can vary across equivalent executions and how that variability affects an observable result.

Do not report a finding solely because raw pointers, manual deletion, callbacks, caches, asynchronous work, or reference counting are present.

## Evidence Requirements

For each elevated candidate provide:

- file and symbol
- owned object and owner
- creation/publication path
- destruction or invalidation path
- retained pointer/reference/callback/container entry
- potential stale access
- thread/task overlap evidence where relevant
- ownership, synchronization, join, guard, or lifecycle mitigation
- relevant application execution path
- downstream application impact
- whether use-after-free or invalid lifetime is established
- whether nondeterministic behavior is established
- confidence
- missing evidence required for confirmation

Prefer a smaller number of well-supported findings over a larger number of speculative candidates.

For this test, do not use previously generated nondeterminism analysis documents, prior analysis artifacts, or prior investigation results.

Perform a new investigation using current CoreStory application intelligence and targeted source inspection.

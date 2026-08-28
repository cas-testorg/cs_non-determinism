# 1. Uninitialized and Indeterminate State

Search for variables, buffers, structs, object members, or pointers that may be consumed before valid initialization on at least one control path.

Include:

- local variables assigned only on some paths
- object members not initialized before use
- partially initialized structs or buffers
- pointers dereferenced before a valid object is established
- sentinel or optional-state values consumed without the required validity check
- indeterminate state that influences a branch, index, size, pointer, calculation, or downstream decision

## Concrete Exemplar

Use the following source pattern as a **concrete exemplar, not as a known defect**.

**File:** `mscts/msutil/msUtil.cc`  
**Symbol:** `msDRClimits`

```cpp
msDRClimits::msDRClimits()
  : _maxFO(-1), _maxELCP(0), _worstTranTerm(0)
{
  _maxLen = _maxCellEm = _maxStageDelay = nwmathFloat::getUninitValue();
  _maxCap.assign(32, nwmathFloat::getUninitValue());
  _maxTran.assign(32, nwmathFloat::getUninitValue());
}
```

A guarded consumer looks like:

```cpp
if (nwmathFloat::isInit(_maxLen) && (len > _maxLen)) {
  return false;
}
```

This example demonstrates a pattern where values that appear "uninitialized" are intentionally represented by a sentinel and are safe when all consumers validate the state before use.

The important investigation question is not merely whether an uninitialized-looking value exists.

The question is whether there is a reachable path where that value is consumed **without the required guard or initialization**.

Use this exemplar to identify semantically equivalent patterns elsewhere in the application.

## Investigation Requirements

For each candidate:

1. Identify the variable, member, buffer, struct field, or pointer whose state is in question.

2. Identify how the state is established:
   - constructor initialization
   - assignment
   - initialization function
   - sentinel value
   - optional-state representation
   - allocation
   - external population

3. Trace all relevant control paths from initialization or missing initialization to the read, dereference, or use.

4. Identify the exact operation that consumes the value.

5. Determine whether a guard, validity predicate, invariant, constructor behavior, or control-flow condition prevents invalid use.

6. Trace the causal chain where supported:

   **missing or invalid initialization**  
   → **reachable read or dereference**  
   → **downstream calculation, branch, pointer use, or state change**  
   → **observable application impact**

7. Distinguish among:
   - intentional sentinel or optional-state handling with correct guards;
   - suspicious initialization pattern that is effectively mitigated;
   - unsupported or incomplete initialization path;
   - established invalid or indeterminate read;
   - established undefined behavior;
   - plausible nondeterministic manifestation requiring additional evidence.

8. For any nondeterminism claim, identify what can vary across equivalent executions and how that variation reaches an observable result.

Do not report a finding solely because:

- a sentinel value is present;
- a member is not initialized directly in a constructor initializer list;
- a pointer is initially null;
- initialization occurs in a separate method;
- static analysis might flag the construct without considering application control flow.

## Evidence Requirements

For each elevated candidate provide:

- file and symbol
- relevant source location
- initialization or missing-initialization path
- read, dereference, or consumer
- relevant application execution path
- guard or mitigation, if present
- whether the local source establishes invalid use
- downstream application impact
- whether undefined behavior is established
- whether nondeterministic behavior is established
- confidence
- missing evidence required for confirmation

Prefer a smaller number of well-supported findings over a larger number of speculative candidates.

For this test, do not use previously generated nondeterminism analysis documents, prior analysis artifacts, or prior investigation results.

Perform a new investigation using current CoreStory application intelligence and targeted source inspection.

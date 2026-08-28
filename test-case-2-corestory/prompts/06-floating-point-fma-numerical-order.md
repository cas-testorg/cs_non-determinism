# 6. Floating-Point, FMA, and Numerical Order Sensitivity

Search for floating-point calculations whose observable result may depend on operand order, reduction order, compiler contraction, instruction selection, or numerical implementation details.

Include:

- floating-point reductions and accumulations
- parallel merges of floating-point partial results
- sums, products, minima/maxima, or gradients whose operand order may vary
- fused multiply-add opportunities
- compiler FP contraction
- fast-math or unsafe-math behavior
- mixed float/double calculations
- numerically unstable comparisons or thresholds where small rounding changes could alter decisions

## Concrete Exemplar

Use the following source pattern as a **concrete exemplar, not as a known defect**.

**File:** `ccd/skewopt/soCG.cc`  
**Symbol:** `soCgDelayCostMtJob::gradFunc`

```cpp
double sumExp = 0;
for (unsigned int j = 0; j < indexVec.size(); ++j) {
  const unsigned int index = indexVec[j];
  const float expVal = exp(vals[j] - max);
  sumExp += expVal;
  tempFloats[index] = expVal;
}
```

This accumulation is mathematically order-independent but floating-point addition is not associative. Different operand orders can therefore produce different rounded results.

The source establishes the order-sensitive arithmetic pattern. It does **not** establish that `indexVec` order actually varies across equivalent executions.

This distinction is the core of the investigation: an order-sensitive calculation is not nondeterministic unless the relevant operand or reduction order can vary.

Use this exemplar to identify semantically equivalent patterns elsewhere in the application.

## Investigation Requirements

For each candidate:

1. Identify the floating-point operation, reduction, accumulation, expression, comparison, or threshold.
2. Identify the exact operands and how their ordering is established.
3. Determine whether operand order, partitioning, merge order, instruction selection, or contraction can vary.
4. For parallel calculations, trace worker partitioning and result-merge order.
5. For FMA/compiler candidates, identify repository evidence for relevant compiler flags, FP contraction settings, target architecture, explicit `std::fma`, or build configuration when available.
6. Determine whether numerical differences can propagate beyond insignificant formatting into a branch, selection, convergence condition, solver result, QoR metric, or other observable application behavior.
7. Identify determinism or stability mechanisms such as:
   - fixed input order
   - fixed worker-index merge order
   - stable partitioning
   - compensated summation
   - explicit FP mode
   - tolerance-aware comparison
   - deterministic final selection
8. Trace the causal chain where supported:

   **variable operand/reduction/instruction behavior**  
   → **floating-point difference**  
   → **downstream threshold, comparison, state, or selection**  
   → **observable application result**

9. Classify each candidate as:
   - confirmed equivalent-run numerical nondeterminism;
   - order-sensitive arithmetic with plausible variable ordering;
   - compiler/build/platform numerical sensitivity only;
   - order-sensitive arithmetic with fixed deterministic ordering;
   - insufficient evidence.

Do not report a finding solely because floating-point arithmetic is present or because an expression could theoretically compile to FMA.

## Evidence Requirements

For each elevated candidate provide:

- file and symbol
- numerical operation
- source of possible order/instruction variation
- evidence that the order or implementation can vary
- downstream consumer or threshold
- determinism/stability mitigation
- relevant application execution path
- observable impact
- whether equivalent-run nondeterminism is established
- whether the result is instead build/platform/compiler sensitivity
- confidence
- missing evidence required for confirmation

Prefer a smaller number of well-supported findings over a larger number of speculative candidates.

For this test, do not use previously generated nondeterminism analysis documents, prior analysis artifacts, or prior investigation results.

Perform a new investigation using current CoreStory application intelligence and targeted source inspection.

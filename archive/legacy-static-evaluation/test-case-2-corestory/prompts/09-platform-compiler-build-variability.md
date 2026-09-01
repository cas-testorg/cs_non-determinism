# 9. Platform, Compiler, and Build Variability

Search for code whose observable behavior may differ because of compiler optimization, floating-point contraction, architecture, operating system, memory model, conditional compilation, platform APIs, or build configuration.

Include:

- architecture-specific code paths
- OS-specific APIs or conditionals
- compiler-specific behavior
- optimization-sensitive code
- `-O2`, `-O3`, fast-math, unsafe-math, or related settings
- FMA or floating-point contraction
- conditional compilation and build macros
- platform-dependent type sizes, alignment, or ABI assumptions
- memory-model assumptions
- build-time feature selection that changes execution behavior

## Concrete Exemplar

Use the following source pattern as a **concrete exemplar, not as a known defect**.

**File:** `mscts/msmesh/msIncrMerger.cc`  
**Symbol:** `msIncrMerger::mergeNodes`

The implementation uses pointer-ordered sets but explicitly restores stable ordering before downstream processing:

```cpp
std::set<msTreeNode *> mergedNodeSet;
std::set<msTreeNode *> outputNodeSet;

// Copy to vector and sort by node ID to avoid Coverity POINTER_NONDETERMINISM warning
TreeNodeVec nextInputNodes;
for (msTreeNode* node : outputNodeSet) {
  nextInputNodes.push_back(node);
}
std::sort(nextInputNodes.begin(), nextInputNodes.end(), msTreeNodeCompare());
```

This exemplar demonstrates a broader principle: runtime or platform-dependent representation may influence an intermediate ordering, but the application can normalize that representation before observable processing.

The local repository did not provide a stronger exemplar tying a specific compiler flag to confirmed behavioral divergence. Therefore, use this exemplar to learn the causal pattern, but search broadly for **semantically equivalent platform/compiler/build-sensitive mechanisms**, including build files and conditional compilation.

## Investigation Requirements

For each candidate:

1. Identify the platform, compiler, architecture, build flag, macro, ABI, floating-point mode, or configuration dependency.
2. Identify repository evidence that the condition is actually applicable, when available:
   - build scripts
   - compiler flags
   - CMake/Make configuration
   - preprocessor branches
   - target architecture definitions
   - platform wrappers
3. Identify the code whose behavior changes under that condition.
4. Trace whether the difference affects:
   - arithmetic
   - ordering
   - synchronization
   - data representation
   - selected algorithm
   - control flow
   - external output
5. Identify normalization, stable ordering, tolerance handling, compatibility layers, or other mitigations.
6. Distinguish carefully among:
   - equivalent-run nondeterminism under the same build and environment;
   - build sensitivity;
   - compiler sensitivity;
   - platform sensitivity;
   - configuration sensitivity.
7. Trace the causal chain where supported:

   **platform/compiler/build difference**  
   → **different code path, instruction behavior, representation, or ordering**  
   → **downstream state, calculation, or decision**  
   → **observable application difference**

8. Classify each candidate as:
   - confirmed platform/compiler/build-sensitive application behavior;
   - plausible sensitivity requiring additional build/runtime evidence;
   - sensitivity with effective normalization or mitigation;
   - equivalent-run nondeterminism separately established;
   - insufficient evidence.

Do not classify a difference between builds, platforms, compiler versions, or configurations as equivalent-run nondeterminism unless the same execution conditions can still produce varying results.

Do not infer applicability of a compiler option solely because code could theoretically be affected by it. Ground the relevant build or configuration evidence where possible.

## Evidence Requirements

For each elevated candidate provide:

- file and symbol
- platform/compiler/build mechanism
- applicable flag, macro, architecture, or configuration evidence
- affected operation or code path
- relevant application execution path
- downstream application impact
- normalization or mitigation
- classification as equivalent-run ND vs build/compiler/platform/configuration sensitivity
- confidence
- missing build, runtime, environment, or compiler evidence required for confirmation

Prefer a smaller number of well-supported findings over a larger number of speculative candidates.

For this test, do not use previously generated nondeterminism analysis documents, prior analysis artifacts, or prior investigation results.

Perform a new investigation using current CoreStory application intelligence and targeted source inspection.

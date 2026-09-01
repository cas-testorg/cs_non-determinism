# Race Conditions

Identify code executed in parallel (OpenMP, TBB, std::thread) that modifies shared, non-thread-local state. Return the shared variables and the parallel execution site.

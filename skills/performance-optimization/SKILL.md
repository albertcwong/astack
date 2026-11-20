---
name: performance-optimization
description: Use when users report slowness, a benchmark regresses, or a performance budget needs verification. Profile browser, service, database or batch workloads and compare a targeted fix with a reproducible baseline.
---

# Performance optimization

Start with the operation the user is waiting for. Name the metric and the target before changing code: for example, p95 search latency at a stated concurrency, peak memory for an import, or time to render the first result. Use a project budget if one exists. If you cannot reproduce the symptom or establish a baseline, report what evidence is missing rather than guessing at a fix.

1. **Record a baseline.** Use the project's benchmark or a small repeatable command on representative, non-sensitive fixtures. Record the revision, build mode, hardware, input size, concurrency and cache state. Measure cold starts separately from steady-state work. Repeat runs and record the sample count and spread, not just the fastest run. Do not run load tests against shared or production systems without specific authorization.
2. **Locate the cost.** For slow initial page loads, inspect the network waterfall and largest contentful paint; for a slow click, inspect the main-thread trace. For an API, separate queue time, application work and database time. Count queries as input grows before assuming an index is missing. For batch work, time stages and check peak memory. Use existing tools and collect only the trace needed to distinguish the likely causes.
3. **Change one thing.** State a prediction: for example, batching lookups should reduce one query per result to a bounded number without changing which results are returned. Check the tradeoff the fix introduces: batching can increase peak memory, an index adds write cost, and caching requires correct tenant and permission boundaries plus a freshness policy.
4. **Repeat the original measurement.** Use the same workload, build settings, cache state and sampling method. Check outputs and run the applicable correctness tests. Keep a change only if the improvement matters, exceeds ordinary variation and preserves behavior. If it does not, discard only your experiment and record why. A faster microbenchmark alone does not prove the user's operation got faster.
5. **Guard the result.** Prefer a stable check such as query count for a fixed fixture or an existing performance budget. Do not turn one laptop timing into a CI threshold. For user-facing changes, distinguish controlled measurements from existing field measurements; if you have no field evidence, do not claim a production improvement.

In the PR or handoff, include the reproduction command, before and after values with units and variability, the bottleneck, the correctness check and the keep/discard decision. Report unsuccessful experiments too.

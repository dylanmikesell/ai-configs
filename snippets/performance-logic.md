# Performance Logic

## 3. Performance & Optimization
- **Efficiency:** Always optimize loops and identify potential performance bottlenecks.
- **Parallelism:** Use concurrency/parallelism (`multiprocessing`, `dask`, or `numba`) whenever beneficial.
- **Justification:** When suggesting a parallelization strategy, explain why the specific tool (e.g., Numba for JIT vs. Dask for distributed arrays) is the best fit for that use case.

# Remaining Tasks - Everything2MD Async Processing

## 1. Completed
- [x] Refactor `server.py` to use `asyncio` and `ThreadPoolExecutor` (via `to_thread`).
- [x] Extract conversion logic into helper functions.
- [x] Verify async dispatch with test script.

## 2. Future Improvements (Out of Scope)
- **Progress Reporting**: Implement a mechanism to report conversion progress (e.g., "Converting page 1/10") back to the client.
- **Job Queue**: For very high loads, replace simple thread pool with a persistent job queue (Redis/Celery).
- **Cancelation**: Allow users to cancel running conversions.

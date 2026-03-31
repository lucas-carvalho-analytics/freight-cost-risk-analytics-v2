#!/bin/sh
set -e

WEB_CONCURRENCY="${WEB_CONCURRENCY:-2}"
LOG_LEVEL="${LOG_LEVEL:-info}"

exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers "${WEB_CONCURRENCY}" --log-level "${LOG_LEVEL}"

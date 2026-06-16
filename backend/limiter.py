"""Shared rate limiter.

Defined in its own module so both `main.py` (to register the handler and
middleware) and route modules (to apply per-route limits) can import the same
Limiter instance without a circular import.

Limits are keyed by client IP. Note: the default in-memory store is per-process;
for multi-worker deployments back it with Redis via `storage_uri`.
"""
import os
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["120/minute"],
    storage_uri=os.getenv("RATELIMIT_STORAGE_URI"),  # e.g. redis://... in prod
)

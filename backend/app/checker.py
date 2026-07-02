import time
from dataclasses import dataclass

import httpx


@dataclass
class CheckResult:
    status_code: int | None
    response_time_ms: int | None
    is_up: bool
    error: str | None


async def check_url(client: httpx.AsyncClient, url: str) -> CheckResult:
    """Ping a single URL and classify the outcome.

    A strict per-request timeout keeps one slow/hanging URL from stalling
    the rest of the batch.
    """
    start = time.perf_counter()
    try:
        response = await client.get(url, follow_redirects=True)
    except httpx.TimeoutException:
        return CheckResult(None, None, False, "Request timed out")
    except httpx.RequestError:
        return CheckResult(None, None, False, "Connection failed")

    elapsed_ms = int((time.perf_counter() - start) * 1000)
    is_up = response.status_code < 400
    error = None if is_up else f"HTTP {response.status_code}"
    return CheckResult(response.status_code, elapsed_ms, is_up, error)

"""Health check view — checks DB and Redis connectivity."""
import time
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache


def health_check(request):
    """
    GET /api/health/
    Returns 200 if all services are up, 503 if any are down.
    Used by load balancers, Docker healthcheck, and uptime monitoring.
    """
    checks = {}
    status_code = 200

    # ── Database ──
    t0 = time.monotonic()
    try:
        connection.ensure_connection()
        connection.cursor().execute("SELECT 1")
        checks["database"] = {"status": "ok", "latency_ms": round((time.monotonic() - t0) * 1000, 1)}
    except Exception as e:
        checks["database"] = {"status": "error", "error": str(e)}
        status_code = 503

    # ── Redis ──
    t0 = time.monotonic()
    try:
        cache.set("health_check_ping", "pong", timeout=5)
        result = cache.get("health_check_ping")
        if result == "pong":
            checks["redis"] = {"status": "ok", "latency_ms": round((time.monotonic() - t0) * 1000, 1)}
        else:
            checks["redis"] = {"status": "error", "error": "ping/pong mismatch"}
            status_code = 503
    except Exception as e:
        checks["redis"] = {"status": "error", "error": str(e)}
        status_code = 503

    return JsonResponse({
        "status": "healthy" if status_code == 200 else "unhealthy",
        "checks": checks,
    }, status=status_code)

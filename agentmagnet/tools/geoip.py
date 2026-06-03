"""IP→Country detection using free ip-api.com (no API key needed).
For AI agents, their IP is their CLOUD SERVER location, not the end user.
Only use IP as fallback. Best: agent sets country via set_preference()."""

import json
import urllib.request
import urllib.error

# LRU cache: ip -> country or None (TTL 1 hour)
_ip_cache: dict[str, str | None] = {}

# Testing override (no network)
FORCE_COUNTRY: str | None = None


def set_force_country(country: str | None):
    """Override for testing. Set to 'es' to test Spain behavior without real IP."""
    global FORCE_COUNTRY
    FORCE_COUNTRY = country


def detect_country_from_ip(ip: str, timeout: int = 3) -> str | None:
    """Detect country from IP using ip-api.com. Returns ISO code (es, mx, us, de...) or None."""
    if FORCE_COUNTRY:
        return FORCE_COUNTRY

    if not ip or ip in ("127.0.0.1", "::1", "localhost", ""):
        return None

    # Private IP ranges
    if ip.startswith(("10.", "192.168.", "172.16.")):
        return None

    # Check cache
    if ip in _ip_cache:
        return _ip_cache[ip]

    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,countryCode"
        req = urllib.request.Request(url, headers={"User-Agent": "AgentMagnet/2.8"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())
            if data.get("status") == "success":
                country = data["countryCode"].lower()
                _ip_cache[ip] = country
                return country
    except Exception:
        pass

    _ip_cache[ip] = None
    return None


def get_client_ip_from_headers(headers: dict) -> str | None:
    """Extract real client IP from HTTP request headers."""
    # X-Forwarded-For: client, proxy1, proxy2
    forwarded = headers.get("x-forwarded-for") or headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    # X-Real-IP: common in nginx/reverse proxies
    real_ip = headers.get("x-real-ip") or headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    # CF-Connecting-IP: Cloudflare
    cf = headers.get("cf-connecting-ip") or headers.get("CF-Connecting-IP")
    if cf:
        return cf.strip()
    return None


def detect_country(agent_id: str | None = None,
                   ip: str | None = None,
                   profile_country: str | None = None,
                   agent_profile=None) -> str | None:
    """Best-effort country detection. Priority:
    1. Agent profile (set_preference)
    2. Explicit IP geolocation
    3. None (caller handles with error message)
    """
    # 1. Agent profile
    if profile_country:
        return profile_country

    if agent_id and agent_profile:
        try:
            pref = agent_profile.get_profile(agent_id)
            if pref and "preferences" in pref:
                c = pref["preferences"].get("country")
                if c:
                    return c
        except Exception:
            pass

    # 2. IP geolocation
    if ip:
        detected = detect_country_from_ip(ip)
        if detected:
            return detected

    return None

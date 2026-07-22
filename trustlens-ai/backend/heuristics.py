from urllib.parse import urlparse

SUSPICIOUS_TLDS = {"tk", "ml", "ga", "cf", "gq", "xyz", "top"}
COMMON_BRANDS = ["paypal", "amazon", "google", "microsoft", "netflix", "paytm", "linkedin"]
URGENCY_PHRASES = [
    "act now", "verify your account", "confirm your identity",
    "suspended", "limited time", "final notice",
    "your account will be closed", "click here immediately", "urgent",
]

PAYMENT_PHRASES = [
    "registration fee", "processing fee", "pay to confirm", "advance payment",
    "wire transfer", "gift card", "convenience fee",
    "refundable deposit", "confirm your interview", "security deposit",
]



def _levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            cur[j] = min(
                prev[j] + 1,               # deletion
                cur[j - 1] + 1,             # insertion
                prev[j - 1] + (ca != cb),   # substitution (0 cost if same char)
            )
        prev = cur
    return prev[-1]


def check_brand_lookalike(host: str) -> list[dict]:
    findings = []
    labels = host.split(".")
    registrable_core = labels[-2] if len(labels) >= 2 else host

    # Check the whole core AND each hyphen-separated piece individually —
    # "paypa1-secure-verify" needs to be broken into ["paypa1", "secure", "verify"]
    # before comparing to "paypal", or the edit distance is thrown off by the
    # unrelated extra words.
    segments = {registrable_core} | set(registrable_core.split("-"))

    for brand in COMMON_BRANDS:
        matched = False
        for seg in segments:
            if not seg:
                continue
            if brand in seg and seg != brand:
                findings.append({
                    "signal": "brand_in_domain",
                    "detail": f"Contains brand name '{brand}' but isn't the official domain",
                    "weight": 20,
                })
                matched = True
                break
            dist = _levenshtein(seg, brand)
            if 0 < dist <= 2 and len(brand) > 4:
                findings.append({
                    "signal": "brand_lookalike",
                    "detail": f"'{seg}' closely resembles '{brand}' ({dist} character difference)",
                    "weight": 22,
                })
                matched = True
                break
        if matched:
            break

    return findings
def check_text_signals(text: str) -> list[dict]:
    if not text:
        return []
    lower = text.lower()
    findings = []

    urgency_hits = [p for p in URGENCY_PHRASES if p in lower]
    if urgency_hits:
        findings.append({
            "signal": "urgency_language",
            "detail": f"Urgency/pressure language detected ({len(urgency_hits)} phrase(s))",
            "weight": min(10 + 5 * len(urgency_hits), 25),
        })

    payment_hits = [p for p in PAYMENT_PHRASES if p in lower]
    if payment_hits:
        findings.append({
            "signal": "upfront_payment_request",
            "detail": f"Requests upfront payment or fees ({len(payment_hits)} phrase(s))",
            "weight": min(15 + 8 * len(payment_hits), 35),
        })

    return findings
def check_url_structure(url: str) -> list[dict]:
    findings = []
    parsed = urlparse(url if "://" in url else f"http://{url}")
    host = (parsed.hostname or "").lower()
    if not host:
        return findings

    tld = host.rsplit(".", 1)[-1]
    if tld in SUSPICIOUS_TLDS:
        findings.append({
            "signal": "suspicious_tld",
            "detail": f"Uses commonly-abused TLD .{tld}",
            "weight": 12,
        })

    findings += check_brand_lookalike(host)
    return findings
def compute_heuristic_score(findings: list[dict]) -> dict:
    raw_score = sum(f["weight"] for f in findings)
    capped_score = min(raw_score, 70)

    if capped_score >= 45:
        level = "HIGH"
    elif capped_score >= 20:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {"score": capped_score, "level": level}
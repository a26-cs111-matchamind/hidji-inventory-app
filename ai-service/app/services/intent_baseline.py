import re
import time
from app.config import settings
from app.schemas import IntentLabel, IntentResponse, IntentScore
from app.services.kb_loader import get_knowledge_base


SLANG_MAP: dict[str, str] = {
    "brp": "berapa",
    "brpa": "berapa",
    "yg": "yang",
    "bkn": "bukan",
    "bikin": "buat",
    "bikinin": "buat",
    "buatin": "buat",
    "pesen": "pesan",
    "pesenin": "pesan",
    "orderin": "order",
    "hbs": "habis",
    "abiz": "habis",
    "abis": "habis",
    "draf": "draf",
    "draft": "draf",
    "wa": "whatsapp",
    "gmn": "bagaimana",
    "gimana": "bagaimana",
    "krg": "kurang",
    "dtg": "datang",
    "bgt": "banget",
    "min": "minimum",
    "stok": "stok",
    "stock": "stok",
    "slisih": "selisih",
    "tumpah": "tumpah",
}

INTENT_PATTERNS: dict[IntentLabel, list[tuple[str, float]]] = {
    "cek_stok": [
        (r"\bsisa\b", 0.40),
        (r"\bberapa\b", 0.25),
        (r"\bce[k]?\b", 0.25),
        (r"\bstok\b", 0.25),
        (r"\btinggal\b", 0.30),
        (r"\baman\b", 0.20),
        (r"\bmenipis\b", 0.25),
        (r"\bhabis\b", 0.20),
    ],
    "minta_rekomendasi": [
        (r"\brekomendasi\b", 0.50),
        (r"\bsaran\b", 0.45),
        (r"\brestock\b", 0.35),
        (r"\bbeli\b", 0.30),
        (r"\bperlu\b", 0.20),
        (r"\bprioritas\b", 0.35),
        (r"\bprediksi\b", 0.35),
        (r"\bbesok\b", 0.20),
    ],
    "buat_draf_pesanan": [
        (r"\bdraf\b", 0.55),
        (r"\bwhatsapp\b", 0.45),
        (r"\bsupplier\b", 0.35),
        (r"\bpesan\b", 0.35),
        (r"\border\b", 0.35),
        (r"\bkirim\b", 0.25),
        (r"\bbuat\b", 0.15),
    ],
    "tanya_resep_sop": [
        (r"\bresep\b", 0.50),
        (r"\btakaran\b", 0.50),
        (r"\bkomposisi\b", 0.45),
        (r"\bsop\b", 0.45),
        (r"\bmenu\b", 0.35),
        (r"\bkena\b", 0.25),
        (r"\bterdampak\b", 0.35),
        (r"\bpakai\b", 0.20),
        (r"\bvarian\b", 0.30),
        (r"\bgram\b|\bml\b", 0.20),
    ],
    "lapor_kendala_stok": [
        (r"\btumpah\b", 0.55),
        (r"\brusak\b", 0.50),
        (r"\bbasi\b", 0.55),
        (r"\bkadaluarsa\b|\bexpired\b", 0.55),
        (r"\bselisih\b", 0.45),
        (r"\blapor\b", 0.35),
        (r"\bbocor\b", 0.50),
        (r"\bhilang\b", 0.40),
    ],
    "di_luar_konteks": [
        (r"\bcuaca\b", 0.55),
        (r"\bpolitik\b|\bpresiden\b", 0.60),
        (r"\bbola\b|\bsepakbola\b", 0.55),
        (r"\bgosip\b|\bartis\b", 0.60),
        (r"\bcoding\b|\bpython\b|\bjavascript\b", 0.55),
        (r"\bresep nasi goreng\b|\bresep rendang\b", 0.65),
        (r"\bhalo\b|\bhai\b|\bselamat pagi\b", 0.30),
    ],
}


def normalize_text(raw_text: str) -> str:
    cleaned = re.sub(r"[^\w\s]", " ", raw_text.lower())
    tokens = [SLANG_MAP.get(tok, tok) for tok in cleaned.split()]
    return " ".join(tokens)


def classify_intent(text: str, top_k: int = 3) -> IntentResponse:
    started = time.perf_counter()
    normalized = normalize_text(text)
    kb = get_knowledge_base()
    entities = kb.find_materials_in_text(normalized)
    menus = kb.find_menus_in_text(normalized)

    raw_scores: dict[IntentLabel, float] = {}
    for label, patterns in INTENT_PATTERNS.items():
        score = 0.0
        for pattern, weight in patterns:
            if re.search(pattern, normalized):
                score += weight
        raw_scores[label] = score

    # Boost domain intents when known Hidji materials or menus are referenced
    if entities:
        raw_scores["cek_stok"] += 0.12
    if menus:
        raw_scores["tanya_resep_sop"] += 0.30

    total = sum(raw_scores.values())
    if total == 0.0:
        # Unrecognized queries with no domain keywords default to out-of-context
        raw_scores["di_luar_konteks"] = 0.72
        raw_scores["cek_stok"] = 0.14
        raw_scores["tanya_resep_sop"] = 0.14
        total = 1.0

    # Softmax-like proportional normalization with smoothing so scores sum cleanly to 1.0
    probs: dict[IntentLabel, float] = {}
    for label, val in raw_scores.items():
        probs[label] = round(val / total, 4)

    ranked = sorted(probs.items(), key=lambda kv: kv[1], reverse=True)
    top_intent, top_conf = ranked[0]

    # Scale confidence slightly upward for strong unambiguous hits while keeping <= 0.99
    if raw_scores[top_intent] >= 0.6 and top_conf < 0.85:
        top_conf = round(min(0.96, top_conf + 0.18), 2)
    else:
        top_conf = round(min(0.99, top_conf), 2)

    top_scores = [IntentScore(intent=lbl, confidence=round(sc, 2)) for lbl, sc in ranked[:top_k]]
    if top_scores:
        top_scores[0] = IntentScore(intent=top_intent, confidence=top_conf)

    elapsed_ms = round((time.perf_counter() - started) * 1000.0, 2)

    return IntentResponse(
        intent=top_intent,
        confidence=top_conf,
        needs_clarification=top_conf < 0.60,
        normalized_text=normalized,
        entities=entities,
        top_k=top_scores,
        model_version=settings.intent_model_version,
        latency_ms=elapsed_ms,
    )

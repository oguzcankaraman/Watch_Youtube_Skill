"""NLP-powered timestamp extraction with a self-learning keyword store."""

import json
import logging
from pathlib import Path

from . import KeywordEntry, KeywordStore, SmartTimestamp, TranscriptEntry

logger = logging.getLogger(__name__)

STORE_PATH = Path(__file__).parent.parent / "data" / "keyword_store.json"
SILENCE_GAP_DEFAULT = 5.0
MIN_SPACING = 2.0

_BUILTIN_KEYWORDS: list[tuple[str, float]] = [
    ("look at", 1.0),
    ("here we see", 1.0),
    ("here we have", 1.0),
    ("here we go", 0.9),
    ("as shown", 1.0),
    ("as you can see", 1.0),
    ("let me show", 1.0),
    ("i'll show you", 0.9),
    ("notice", 0.9),
    ("zoom in", 1.0),
    ("zoom out", 0.9),
    ("diagram", 1.0),
    ("graph", 1.0),
    ("chart", 1.0),
    ("code", 0.9),
    ("screen", 0.9),
    ("table", 0.9),
    ("slide", 0.9),
    ("formula", 1.0),
    ("equation", 1.0),
    ("this is", 0.7),
    ("this shows", 1.0),
    ("this represents", 1.0),
    ("right here", 1.0),
    ("over here", 1.0),
    ("highlight", 0.9),
    ("point to", 1.0),
    ("click on", 0.9),
    ("terminal", 1.0),
    ("output", 0.8),
    ("result", 0.7),
    ("example", 0.7),
    ("demo", 0.9),
    ("visualization", 1.0),
    ("plot", 0.9),
    ("architecture", 0.9),
    ("pipeline", 0.9),
    ("screenshot", 1.0),
]

_DEFAULT_DOMAIN_CLUSTERS: dict[str, list[str]] = {
    "coding": ["function", "variable", "class", "method", "import", "error", "debug", "refactor"],
    "math": ["integral", "derivative", "matrix", "vector", "proof", "theorem", "solve"],
    "data": ["dataset", "column", "row", "model", "accuracy", "loss", "training", "inference"],
    "design": ["layout", "component", "color", "margin", "padding", "responsive", "ui"],
}


# ---------------------------------------------------------------------------
# Keyword Store persistence
# ---------------------------------------------------------------------------

def load_keyword_store(path: Path = STORE_PATH) -> KeywordStore:
    if path.exists():
        try:
            raw = json.loads(path.read_text())
            keywords = [KeywordEntry(**k) for k in raw.get("keywords", [])]
            return KeywordStore(
                version=raw.get("version", 1),
                keywords=keywords,
                domain_clusters=raw.get("domain_clusters", _DEFAULT_DOMAIN_CLUSTERS),
            )
        except Exception as e:
            logger.warning(f"Failed to load keyword store ({e}), using defaults")

    return KeywordStore(
        version=1,
        keywords=[KeywordEntry(phrase=p, weight=w, source="builtin") for p, w in _BUILTIN_KEYWORDS],
        domain_clusters=_DEFAULT_DOMAIN_CLUSTERS,
    )


def save_keyword_store(store: KeywordStore, path: Path = STORE_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "version": store.version,
        "keywords": [
            {"phrase": k.phrase, "weight": k.weight, "source": k.source, "occurrences": k.occurrences}
            for k in store.keywords
        ],
        "domain_clusters": store.domain_clusters,
    }
    path.write_text(json.dumps(data, indent=2))


# ---------------------------------------------------------------------------
# Main extraction entry point
# ---------------------------------------------------------------------------

def extract_smart_timestamps(
    entries: list[TranscriptEntry],
    silence_threshold: float = SILENCE_GAP_DEFAULT,
    max_timestamps: int = 50,
    store_path: Path = STORE_PATH,
) -> list[SmartTimestamp]:
    """Run Rule A (NLP keywords) + Rule B (silence gaps), deduplicate, cap."""
    if not entries:
        return []

    store = load_keyword_store(store_path)

    keyword_ts = _extract_keyword_timestamps(entries, store)
    silence_ts = _extract_silence_timestamps(entries, silence_threshold)

    combined = keyword_ts + silence_ts
    deduped = _deduplicate_timestamps(combined, MIN_SPACING)

    if len(deduped) > max_timestamps:
        kw = [t for t in deduped if "keyword" in t.reason or "spacy" in t.reason or "combined" in t.reason]
        sil = [t for t in deduped if t not in kw]
        sil.sort(key=lambda t: _silence_gap_seconds(t.reason), reverse=True)
        deduped = (kw + sil)[:max_timestamps]
        deduped.sort(key=lambda t: t.time_sec)

    if not deduped and entries:
        deduped = _fallback_timestamps(entries)

    return deduped


# ---------------------------------------------------------------------------
# Rule A — keyword matching (spaCy + learned store)
# ---------------------------------------------------------------------------

def _extract_keyword_timestamps(
    entries: list[TranscriptEntry],
    store: KeywordStore,
) -> list[SmartTimestamp]:
    """Match transcript entries against keyword store using spaCy NLP."""
    nlp = _get_spacy_nlp()
    results: list[SmartTimestamp] = []

    all_phrases = {k.phrase.lower(): k for k in store.keywords}
    # Flatten domain cluster terms with lower weight
    cluster_terms: dict[str, float] = {}
    for terms in store.domain_clusters.values():
        for t in terms:
            cluster_terms[t.lower()] = 0.6

    for entry in entries:
        text_lower = entry.text.lower()
        matched_reason: str | None = None
        best_weight = 0.0

        # 1. Direct phrase matching against keyword store
        for phrase, kentry in all_phrases.items():
            if phrase in text_lower and kentry.weight > best_weight:
                matched_reason = f"keyword:{phrase}"
                best_weight = kentry.weight

        # 2. Domain cluster term matching
        if nlp is not None:
            doc = nlp(entry.text)
            for token in doc:
                term = token.lemma_.lower()
                if term in cluster_terms and cluster_terms[term] > best_weight:
                    matched_reason = f"keyword:{term}"
                    best_weight = cluster_terms[term]

            # 3. spaCy structural patterns: imperative deictic phrases
            # e.g. "look", "see", "notice" as verb near demonstrative
            if best_weight < 0.7:
                for token in doc:
                    if token.pos_ == "VERB" and token.lemma_.lower() in (
                        "look", "see", "notice", "observe", "check", "view", "watch",
                    ):
                        # Check for a nearby demonstrative or deictic word
                        context = [t.lower_ for t in doc[max(0, token.i-2):token.i+4]]
                        if any(d in context for d in ("this", "here", "that", "there", "these", "those")):
                            matched_reason = f"spacy:deictic_verb"
                            best_weight = 0.75
                            break

        if matched_reason and best_weight >= 0.6:
            results.append(SmartTimestamp(
                time_sec=entry.start_sec,
                reason=matched_reason,
                transcript_text=entry.text,
            ))

    return results


def _get_spacy_nlp():
    """Load spaCy model, return None if unavailable (graceful degradation)."""
    try:
        import spacy
        return spacy.load("en_core_web_sm")
    except Exception as e:
        logger.warning(f"spaCy unavailable ({e}); falling back to string matching only")
        return None


# ---------------------------------------------------------------------------
# Rule B — silence gap detection
# ---------------------------------------------------------------------------

def _extract_silence_timestamps(
    entries: list[TranscriptEntry],
    threshold: float,
) -> list[SmartTimestamp]:
    """Extract timestamps at midpoints of long silences (>= threshold seconds)."""
    results = []
    for i in range(len(entries) - 1):
        gap = entries[i + 1].start_sec - entries[i].end_sec
        if gap >= threshold:
            midpoint = entries[i].end_sec + gap / 2
            results.append(SmartTimestamp(
                time_sec=midpoint,
                reason=f"silence_gap:{gap:.1f}s",
                transcript_text=entries[i].text,
            ))
    return results


# ---------------------------------------------------------------------------
# Deduplication + fallback
# ---------------------------------------------------------------------------

def _deduplicate_timestamps(
    timestamps: list[SmartTimestamp],
    min_spacing: float,
) -> list[SmartTimestamp]:
    """Remove timestamps within min_spacing seconds; prefer keyword > silence."""
    if not timestamps:
        return []

    timestamps = sorted(timestamps, key=lambda t: t.time_sec)
    kept: list[SmartTimestamp] = [timestamps[0]]

    for ts in timestamps[1:]:
        last = kept[-1]
        if ts.time_sec - last.time_sec < min_spacing:
            # Keep the one with higher priority
            if _reason_priority(ts.reason) > _reason_priority(last.reason):
                kept[-1] = ts
        else:
            kept.append(ts)

    return kept


def _reason_priority(reason: str) -> int:
    if reason.startswith("keyword") or reason.startswith("spacy"):
        return 2
    if reason == "combined":
        return 3
    return 1  # silence_gap


def _silence_gap_seconds(reason: str) -> float:
    if reason.startswith("silence_gap:"):
        try:
            return float(reason.split(":")[1].rstrip("s"))
        except ValueError:
            pass
    return 0.0


def _fallback_timestamps(entries: list[TranscriptEntry]) -> list[SmartTimestamp]:
    """Return 5 evenly-spaced timestamps when NLP finds nothing."""
    n = min(5, len(entries))
    step = max(1, len(entries) // n)
    return [
        SmartTimestamp(
            time_sec=entries[i * step].start_sec,
            reason="fallback:evenly_spaced",
            transcript_text=entries[i * step].text,
        )
        for i in range(n)
    ]


# ---------------------------------------------------------------------------
# Self-learning: update keyword store after a video run
# ---------------------------------------------------------------------------

def update_keyword_store(
    entries: list[TranscriptEntry],
    selected_timestamps: list[SmartTimestamp],
    store_path: Path = STORE_PATH,
    bigram_threshold: float = 0.05,
    unigram_threshold: float = 0.15,
    min_selected_count: int = 2,
) -> int:
    """
    Extract high-TF-IDF terms from transcript windows around selected frames.

    Anti-overfitting rules:
    - Bigrams (e.g. "kernel mode", "page table"): require lift > bigram_threshold.
      Bigrams are naturally specific and generalize well across similar videos.
    - Unigrams (e.g. "kernel"): require lift > unigram_threshold AND the word
      must appear at least min_selected_count times in the selected windows.
      This filters out generic noise words (e.g. "point", "piece", "job") that
      have modest lift but carry no deictic signal.
    """
    if not entries or not selected_timestamps:
        return 0

    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        import numpy as np
    except ImportError:
        logger.warning("scikit-learn not available — skipping keyword store update")
        return 0

    store = load_keyword_store(store_path)
    existing_phrases = {k.phrase.lower() for k in store.keywords}

    # Build "selected" windows (±10s around each timestamp)
    selected_times = {ts.time_sec for ts in selected_timestamps}
    selected_texts: list[str] = []
    background_texts: list[str] = []

    for entry in entries:
        near_selected = any(abs(entry.start_sec - t) <= 10.0 for t in selected_times)
        bucket = selected_texts if near_selected else background_texts
        bucket.append(entry.text)

    if not selected_texts or not background_texts:
        return 0

    selected_blob = " ".join(selected_texts).lower()

    corpus = [" ".join(selected_texts), " ".join(background_texts)]
    try:
        vec = TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=1,
            max_features=300,
            stop_words="english",
        )
        tfidf = vec.fit_transform(corpus)
        feature_names = vec.get_feature_names_out()
        selected_scores = tfidf[0].toarray()[0]
        background_scores = tfidf[1].toarray()[0]
        lift = selected_scores - background_scores
    except Exception as e:
        logger.warning(f"TF-IDF failed: {e}")
        return 0

    added = 0
    for idx in np.argsort(lift)[::-1]:
        phrase = feature_names[idx]
        is_bigram = " " in phrase

        # Apply separate thresholds for unigrams vs bigrams
        threshold = bigram_threshold if is_bigram else unigram_threshold
        if lift[idx] < threshold:
            continue

        # Skip very short or numeric tokens
        if phrase.isnumeric() or len(phrase) < 4:
            continue

        # Unigrams must appear at least min_selected_count times in selected windows
        # (prevents low-frequency noise from squeaking past the lift threshold)
        if not is_bigram:
            count = selected_blob.split().count(phrase)
            if count < min_selected_count:
                continue

        if phrase in existing_phrases:
            for k in store.keywords:
                if k.phrase.lower() == phrase and k.source == "learned":
                    k.occurrences += 1
                    if k.occurrences >= 3 and k.weight < 0.8:
                        k.weight = 0.8
                        logger.info(f"Promoted keyword '{phrase}' to weight 0.8")
            continue

        store.keywords.append(KeywordEntry(
            phrase=phrase,
            weight=0.5,
            source="learned",
            occurrences=1,
        ))
        existing_phrases.add(phrase)
        logger.info(f"Learned keyword: '{phrase}' ({'bigram' if is_bigram else 'unigram'}, lift={lift[idx]:.3f})")
        added += 1
        if added >= 10:
            break

    if added > 0:
        save_keyword_store(store, store_path)

    return added

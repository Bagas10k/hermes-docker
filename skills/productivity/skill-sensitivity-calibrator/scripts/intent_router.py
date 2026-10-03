#!/usr/bin/env python3
"""
Bilingual (ID-EN) Pre-Filter Intent Router for Hermes Skills
Mengalibrasi kepekaan pemanggilan skill dengan pembaruan keyakinan Bayesian,
kamus bahasa Indonesia percakapan, dan penalti konflik konteks.
"""

import os
import re
import sys
import json
import glob
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

SKILLS_ROOT = os.path.expanduser("~/.hermes/skills")

# Kamus Sinonim & Idiom Percakapan Indonesia ke Konsep Teknis
COLLOQUIAL_MAPPING: Dict[str, List[str]] = {
    "chat": ["chat", "conversation", "messaging", "dialog", "tele", "telegram", "obrolan", "pesan", "companion"],
    "desain": ["design", "ui", "ux", "layout", "visual", "bento", "grid", "tampilan", "kosongan", "craft", "komponen"],
    "autopilot": ["autopilot", "autonomous", "self-learning", "riset", "mandiri", "tanpa henti", "siklus", "learner"],
    "backend": ["backend", "server", "api", "database", "pm2", "daemon", "service", "port", "express", "endpoint"],
    "debug": ["debug", "error", "crash", "fix", "rusak", "macet", "benerin", "galat", "symptom", "log"],
    "suara": ["voice", "audio", "speech", "tts", "telepon", "sound", "binaural"],
    "konten": ["carousel", "post", "social", "instagram", "sputarai", "warta", "berita", "feed"],
    "mobile": ["mobile", "responsive", "responsif", "phone", "touch", "ponsel", "layar", "companion", "zen"],
    "web": ["web", "frontend", "html", "css", "interface", "halaman", "antarmuka", "site"],
    "keamanan": ["security", "auth", "sandbox", "token", "rlimit", "guardrail", "aman", "isolasi"],
    "arsitektur": ["architecture", "arsitektur", "decision", "trade-off", "system", "mindset", "struktur"]
}

# Akhiran/Stemming umum bahasa Indonesia -> Inggris
STEM_MAP = {
    "responsif": "responsive",
    "interaktif": "interactive",
    "kreatif": "creative",
    "otomatis": "automatic",
    "otomasi": "automation",
    "arsitektur": "architecture",
    "analisis": "analysis",
    "komprehensif": "comprehensive",
    "sistem": "system",
    "spasial": "spatial"
}

# Penalti Negatif jika Konteks Bertentangan
NEGATIVE_RULES = [
    # Jika konteks server/daemon murni, kurangi skor skill grafis berat / audio
    (r"\b(server|pm2|daemon|terminal|cli|bash|ssh|rlimit|cgroups)\b", r"(p5js|threejs|manim|binaural|songsee|gif)", -0.50),
    # Jika konteks database/backend, kurangi skill visual/motion
    (r"\b(database|sqlite|sql|query|postgres|redis|migration)\b", r"(kinetic-typography|shader-canvas|spring-physics)", -0.45),
    # Jika konteks audio/suara, kurangi skill bento grid / dasbor
    (r"\b(tts|voice|suara|telepon|audio|speech)\b", r"(bento-grid|database-design|codebase-inspection)", -0.40)
]

TIER_THRESHOLDS = {
    "strict": 0.65,
    "balanced": 0.40,
    "sensitive": 0.25
}

@dataclass
class SkillMeta:
    name: str
    category: str
    description: str
    path: str
    tags: List[str] = field(default_factory=list)

@dataclass
class ScoredSkill:
    name: str
    category: str
    score: float
    confidence: str
    matched_reasons: List[str]
    description_preview: str

class IntentRouter:
    def __init__(self, skills_root: str = SKILLS_ROOT):
        self.skills_root = skills_root
        self.skills_index: Dict[str, SkillMeta] = {}
        self._load_index()

    def _load_index(self):
        pattern = os.path.join(self.skills_root, "**", "SKILL.md")
        files = glob.glob(pattern, recursive=True)
        for fpath in files:
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read(1500)
                
                name_match = re.search(r"^name:\s*([a-zA-Z0-9_-]+)", content, re.MULTILINE)
                desc_match = re.search(r"^description:\s*([^\n]+)", content, re.MULTILINE)
                
                if name_match:
                    skill_name = name_match.group(1).strip()
                    desc = desc_match.group(1).strip().strip('"\'') if desc_match else ""
                    rel_dir = os.path.dirname(os.path.relpath(fpath, self.skills_root))
                    category = rel_dir.split(os.sep)[0] if rel_dir else "general"

                    # Parse tags
                    tags = []
                    tags_match = re.search(r"tags:\s*\[(.*?)\]", content)
                    if tags_match:
                        tags = [t.strip().strip('"\'') for t in tags_match.group(1).split(",")]

                    self.skills_index[skill_name] = SkillMeta(
                        name=skill_name,
                        category=category,
                        description=desc,
                        path=fpath,
                        tags=tags
                    )
            except Exception:
                continue

    def route(self, query: str, tier: str = "balanced", top_k: int = 3) -> List[ScoredSkill]:
        threshold = TIER_THRESHOLDS.get(tier.lower(), 0.40)
        q_lower = query.lower()
        raw_tokens = set(re.findall(r"\b[a-zA-Z0-9_-]+\b", q_lower))
        q_tokens = set(raw_tokens)
        for t in raw_tokens:
            if t in STEM_MAP:
                q_tokens.add(STEM_MAP[t])

        # 1. Ekstraksi sinonim percakapan Indonesia
        expanded_intents = set()
        for token in q_tokens:
            for concept, synonyms in COLLOQUIAL_MAPPING.items():
                if token in synonyms or any(s in token for s in synonyms if len(s) >= 3):
                    expanded_intents.add(concept)
                    expanded_intents.update(synonyms)

        scored_list: List[ScoredSkill] = []

        for name, meta in self.skills_index.items():
            score = 0.0
            reasons = []
            name_lower = name.lower()
            desc_lower = meta.description.lower()

            # A. Exact name matching (Weight: 0.40)
            if name_lower in q_lower or any(t == name_lower for t in q_tokens):
                score += 0.40
                reasons.append(f"Cocok nama eksplisit '{name}'")
            elif any(t in name_lower.split("-") for t in q_tokens if len(t) >= 3):
                score += 0.20
                reasons.append(f"Sebagian kata nama cocok")

            # B. Description & Trigger 'Use when' matching (Weight: 0.30)
            use_when_match = re.search(r"use when\s+([^.]+)", desc_lower)
            trigger_text = use_when_match.group(1) if use_when_match else desc_lower[:70]
            matched_desc_tokens = [t for t in q_tokens if len(t) >= 3 and t in trigger_text]
            if matched_desc_tokens:
                sub_score = min(0.30, len(matched_desc_tokens) * 0.12)
                score += sub_score
                reasons.append(f"Trigger deskripsi cocok ({', '.join(matched_desc_tokens)})")

            # C. Indonesian Colloquial & Synonym Matching (Weight: 0.25)
            matched_syns = [c for c in expanded_intents if len(c) >= 3 and (c in name_lower or c in desc_lower)]
            if matched_syns:
                syn_score = min(0.25, len(matched_syns) * 0.08)
                score += syn_score
                reasons.append(f"Kamus dwibahasa cocok: {matched_syns[:3]}")

            # D. Tags matching (Weight: 0.15)
            if meta.tags:
                matched_tags = [t for t in meta.tags if t.lower() in q_lower or t.lower() in expanded_intents]
                if matched_tags:
                    score += 0.15
                    reasons.append(f"Tag relevan ({', '.join(matched_tags)})")

            # E. Negative Rules (Anti-Conflict Penalty)
            for ctx_pattern, skill_pattern, penalty in NEGATIVE_RULES:
                if re.search(ctx_pattern, q_lower) and re.search(skill_pattern, name_lower):
                    score += penalty
                    reasons.append(f"Penalti konflik domain ({penalty})")

            # Normalisasi bounded [0.0, 1.0]
            score = max(0.0, min(1.0, score))

            if score >= threshold:
                confidence = "HIGH" if score >= 0.65 else ("MEDIUM" if score >= 0.40 else "LOW")
                scored_list.append(ScoredSkill(
                    name=name,
                    category=meta.category,
                    score=round(score, 3),
                    confidence=confidence,
                    matched_reasons=reasons,
                    description_preview=meta.description[:90] + ("..." if len(meta.description) > 90 else "")
                ))

        # Urutkan berdasarkan skor tertinggi
        scored_list.sort(key=lambda s: s.score, reverse=True)

        # VOI Pruning: Jika top-1 dominan (margin > 0.30 dibanding top-2), pangkas top-2 dan top-3
        if len(scored_list) >= 2 and (scored_list[0].score - scored_list[1].score) >= 0.30:
            return scored_list[:1]

        return scored_list[:top_k]

def main():
    if len(sys.argv) < 2:
        print("Penggunaan: intent_router.py [--tier strict|balanced|sensitive] <kueri percakapan>")
        sys.exit(1)

    tier = "balanced"
    args = sys.argv[1:]
    if args[0] in ["--tier", "-t"] and len(args) > 2:
        tier = args[1]
        query = " ".join(args[2:])
    else:
        query = " ".join(args)

    router = IntentRouter()
    results = router.route(query, tier=tier)

    output = {
        "query": query,
        "sensitivity_tier": tier,
        "threshold": TIER_THRESHOLDS.get(tier, 0.40),
        "total_skills_indexed": len(router.skills_index),
        "matched_count": len(results),
        "recommendations": [
            {
                "skill": r.name,
                "category": r.category,
                "score": r.score,
                "confidence": r.confidence,
                "reasons": r.matched_reasons,
                "desc": r.description_preview
            } for r in results
        ]
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()

import json
import os
import re
from typing import Any, Dict, List

import httpx


INFERENCE_URL = "https://inference.do-ai.run/v1/chat/completions"
MODEL = os.getenv("DO_INFERENCE_MODEL", "anthropic-claude-4.6-sonnet")
API_KEY = os.getenv("GRADIENT_MODEL_ACCESS_KEY", os.getenv("DIGITALOCEAN_INFERENCE_KEY", ""))


def _extract_json(text: str) -> str:
    m = re.search(r"```(?:json)?\s*\n?([\s\S]*?)\n?\s*```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    m = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return text.strip()


def _coerce_unstructured_payload(raw_text: str) -> dict[str, object]:
    compact = raw_text.strip()
    normalized = compact.replace("\n", ",")
    tags = [part.strip(" -•\t") for part in normalized.split(",") if part.strip(" -•\t")]
    if not tags:
        tags = ["guided plan", "saved output", "shareable insight"]
    headline = tags[0].title()
    items = []
    for index, tag in enumerate(tags[:3], start=1):
        items.append({
            "title": f"Stage {index}: {tag.title()}",
            "detail": f"Use {tag} to move the request toward a demo-ready outcome.",
            "score": min(96, 80 + index * 4),
        })
    highlights = [tag.title() for tag in tags[:3]]
    return {
        "note": "Model returned plain text instead of JSON",
        "raw": compact,
        "text": compact,
        "summary": compact or f"{headline} fallback is ready for review.",
        "tags": tags[:6],
        "items": items,
        "score": 88,
        "insights": [f"Lead with {headline} on the first screen.", "Keep one clear action visible throughout the flow."],
        "next_actions": ["Review the generated plan.", "Save the strongest output for the demo finale."],
        "highlights": highlights,
    }

def _normalize_inference_payload(payload: object) -> dict[str, object]:
    if not isinstance(payload, dict):
        return _coerce_unstructured_payload(str(payload))
    normalized = dict(payload)
    summary = str(normalized.get("summary") or normalized.get("note") or "AI-generated plan ready")
    raw_items = normalized.get("items")
    items: list[dict[str, object]] = []
    if isinstance(raw_items, list):
        for index, entry in enumerate(raw_items[:3], start=1):
            if isinstance(entry, dict):
                title = str(entry.get("title") or f"Stage {index}")
                detail = str(entry.get("detail") or entry.get("description") or title)
                score = float(entry.get("score") or min(96, 80 + index * 4))
            else:
                label = str(entry).strip() or f"Stage {index}"
                title = f"Stage {index}: {label.title()}"
                detail = f"Use {label} to move the request toward a demo-ready outcome."
                score = float(min(96, 80 + index * 4))
            items.append({"title": title, "detail": detail, "score": score})
    if not items:
        items = _coerce_unstructured_payload(summary).get("items", [])
    raw_insights = normalized.get("insights")
    if isinstance(raw_insights, list):
        insights = [str(entry) for entry in raw_insights if str(entry).strip()]
    elif isinstance(raw_insights, str) and raw_insights.strip():
        insights = [raw_insights.strip()]
    else:
        insights = []
    next_actions = normalized.get("next_actions")
    if isinstance(next_actions, list):
        next_actions = [str(entry) for entry in next_actions if str(entry).strip()]
    else:
        next_actions = []
    highlights = normalized.get("highlights")
    if isinstance(highlights, list):
        highlights = [str(entry) for entry in highlights if str(entry).strip()]
    else:
        highlights = []
    if not insights and not next_actions and not highlights:
        fallback = _coerce_unstructured_payload(summary)
        insights = fallback.get("insights", [])
        next_actions = fallback.get("next_actions", [])
        highlights = fallback.get("highlights", [])
    return {
        **normalized,
        "summary": summary,
        "items": items,
        "score": float(normalized.get("score") or 88),
        "insights": insights,
        "next_actions": next_actions,
        "highlights": highlights,
    }


async def _call_inference(messages: List[Dict[str, str]], max_tokens: int = 512) -> Dict[str, Any]:
    if max_tokens < 256:
        max_tokens = 256

    fallback = {
        "note": "AI is temporarily unavailable. Returned a deterministic planning fallback.",
        "summary": "A draft planning brief was generated using local fallback logic.",
        "items": [
            "Problem framing extracted from raw input",
            "Target users inferred from language cues",
            "Solution direction synthesized with constraints",
            "Feature priorities ordered by impact and effort",
        ],
        "score": 68,
        "score_rationale": "Moderate viability based on clear pain signal but incomplete market evidence.",
        "section_traces": {},
        "transformation": {
            "steps": ["ingest", "normalize", "structure", "validate"],
            "lineage": ["raw_input -> normalized_concepts -> brief_sections"]
        }
    }

    if not API_KEY:
        return fallback

    payload = {
        "model": MODEL,
        "messages": messages,
        "max_completion_tokens": 512,
        "temperature": 0.3,
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            resp = await client.post(INFERENCE_URL, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        content = ""
        choices = data.get("choices", [])
        if choices:
            content = choices[0].get("message", {}).get("content", "")

        cleaned = _extract_json(content)
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            parsed.setdefault("note", "AI-generated response")
            return parsed
        return fallback
    except Exception:
        return fallback


async def generate_structured_brief(query: str, preferences: str) -> Dict[str, Any]:
    prompt = {
        "role": "user",
        "content": (
            "You are a product-planning workbench engine. Return JSON only with keys: "
            "summary (string), items (array of concise strings for problem/users/solution/differentiators/feature priorities), "
            "score (int 0-100), score_rationale (string), section_traces (object by section), transformation (object). "
            "Each section trace must include source_phrases (array), assumptions (array), confidence (low|medium|high). "
            f"Raw idea: {query}\n"
            f"Planning preferences: {preferences}\n"
        ),
    }
    return await _call_inference([prompt], max_tokens=512)


async def generate_section_insights(selection: str, context: str) -> Dict[str, Any]:
    prompt = {
        "role": "user",
        "content": (
            "You are a product strategy reviewer. Return JSON only with keys: insights (array), next_actions (array), highlights (array). "
            "Keep it concrete and specific to product planning. "
            f"Selected section: {selection}\n"
            f"Context: {context}\n"
        ),
    }
    result = await _call_inference([prompt], max_tokens=512)

    insights = result.get("insights") if isinstance(result.get("insights"), list) else []
    next_actions = result.get("next_actions") if isinstance(result.get("next_actions"), list) else []
    highlights = result.get("highlights") if isinstance(result.get("highlights"), list) else []

    if not insights:
        insights = ["Section-level AI insights are temporarily unavailable; fallback heuristics applied."]
    if not next_actions:
        next_actions = ["Clarify target segment and success metric before implementation sequencing."]
    if not highlights:
        highlights = [selection[:140]] if selection else ["No selection provided."]

    return {
        "insights": insights,
        "next_actions": next_actions,
        "highlights": highlights,
        "note": result.get("note", "AI-generated response"),
    }

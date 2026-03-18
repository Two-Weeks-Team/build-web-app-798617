import json
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ai_service import generate_section_insights, generate_structured_brief
from models import PlanningArtifact, SectionTrace, get_db


router = APIRouter()


class PlanRequest(BaseModel):
    query: str
    preferences: Optional[str] = ""


class InsightsRequest(BaseModel):
    selection: str
    context: str


@router.post("/plan")
@router.post("/plan")
async def create_plan(payload: PlanRequest, db: Session = Depends(get_db)):
    if not payload.query.strip():
        raise HTTPException(status_code=400, detail="query is required")

    ai_result = await generate_structured_brief(payload.query, payload.preferences or "")

    summary = str(ai_result.get("summary", "Draft brief generated."))
    items = ai_result.get("items", [])
    if not isinstance(items, list):
        items = []
    score = ai_result.get("score", 0)
    try:
        score = int(score)
    except Exception:
        score = 0

    score_rationale = str(ai_result.get("score_rationale", "Viability estimated from available context."))

    title = payload.query.strip().split("\n")[0][:80] or "Untitled planning brief"

    artifact = PlanningArtifact(
        title=title,
        raw_input=payload.query,
        preferences_json=json.dumps({"preferences": payload.preferences or ""}),
        summary=summary,
        items_json=json.dumps(items),
        score=score,
        score_rationale=score_rationale,
        is_seed=False,
        updated_at=datetime.utcnow(),
    )
    db.add(artifact)
    db.flush()

    section_traces = ai_result.get("section_traces", {})
    if isinstance(section_traces, dict):
        for section_key, details in section_traces.items():
            if not isinstance(details, dict):
                continue
            trace = SectionTrace(
                artifact_id=artifact.id,
                section_key=str(section_key),
                source_phrases_json=json.dumps(details.get("source_phrases", [])),
                assumptions_json=json.dumps(details.get("assumptions", [])),
                confidence=str(details.get("confidence", "medium")),
            )
            db.add(trace)

    db.commit()
    db.refresh(artifact)

    return {
        "summary": summary,
        "items": items,
        "score": score,
        "score_rationale": score_rationale,
        "artifact_id": artifact.id,
        "transformation": ai_result.get("transformation", {}),
        "note": ai_result.get("note", "AI-generated response"),
    }


@router.post("/insights")
@router.post("/insights")
async def get_insights(payload: InsightsRequest):
    result = await generate_section_insights(payload.selection, payload.context)
    return {
        "insights": result.get("insights", []),
        "next_actions": result.get("next_actions", []),
        "highlights": result.get("highlights", []),
        "note": result.get("note", "AI-generated response"),
    }


@router.get("/dossiers")
@router.get("/dossiers")
def list_dossiers(db: Session = Depends(get_db)):
    records: List[PlanningArtifact] = (
        db.query(PlanningArtifact)
        .order_by(PlanningArtifact.updated_at.desc())
        .limit(30)
        .all()
    )

    return {
        "items": [
            {
                "id": r.id,
                "title": r.title,
                "summary": r.summary,
                "score": r.score,
                "score_rationale": r.score_rationale,
                "is_seed": r.is_seed,
                "updated_at": r.updated_at.isoformat() if r.updated_at else None,
            }
            for r in records
        ]
    }


@router.get("/dossiers/{artifact_id}")
@router.get("/dossiers/{artifact_id}")
def get_dossier(artifact_id: int, db: Session = Depends(get_db)):
    artifact = db.query(PlanningArtifact).filter(PlanningArtifact.id == artifact_id).first()
    if not artifact:
        raise HTTPException(status_code=404, detail="artifact not found")

    traces = db.query(SectionTrace).filter(SectionTrace.artifact_id == artifact_id).all()

    return {
        "id": artifact.id,
        "title": artifact.title,
        "raw_input": artifact.raw_input,
        "preferences": json.loads(artifact.preferences_json or "{}"),
        "summary": artifact.summary,
        "items": json.loads(artifact.items_json or "[]"),
        "score": artifact.score,
        "score_rationale": artifact.score_rationale,
        "section_traces": [
            {
                "section_key": t.section_key,
                "source_phrases": json.loads(t.source_phrases_json or "[]"),
                "assumptions": json.loads(t.assumptions_json or "[]"),
                "confidence": t.confidence,
            }
            for t in traces
        ],
    }

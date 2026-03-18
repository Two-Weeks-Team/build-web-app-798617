import json
import os
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import Session, declarative_base, relationship, sessionmaker


Base = declarative_base()


def _normalize_database_url(raw_url: str) -> str:
    if raw_url.startswith("postgresql+asyncpg://"):
        return raw_url.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)
    if raw_url.startswith("postgres://"):
        return raw_url.replace("postgres://", "postgresql+psycopg://", 1)
    return raw_url


DATABASE_URL = _normalize_database_url(
    os.getenv("DATABASE_URL", os.getenv("POSTGRES_URL", "sqlite:///./app.db"))
)

connect_args = {}
if not DATABASE_URL.startswith("sqlite"):
    if "localhost" not in DATABASE_URL and "127.0.0.1" not in DATABASE_URL:
        connect_args = {"sslmode": "require"}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class PlanningArtifact(Base):
    __tablename__ = "bw_planning_artifacts"

    id = Integer().with_variant(Integer, "sqlite")
    id = __import__("sqlalchemy").Column(Integer, primary_key=True, index=True)
    title = __import__("sqlalchemy").Column(String(200), nullable=False)
    raw_input = __import__("sqlalchemy").Column(Text, nullable=False)
    preferences_json = __import__("sqlalchemy").Column(Text, default="{}", nullable=False)
    summary = __import__("sqlalchemy").Column(Text, nullable=False)
    items_json = __import__("sqlalchemy").Column(Text, default="[]", nullable=False)
    score = __import__("sqlalchemy").Column(Integer, default=0, nullable=False)
    score_rationale = __import__("sqlalchemy").Column(Text, default="", nullable=False)
    is_seed = __import__("sqlalchemy").Column(Boolean, default=False, nullable=False)
    created_at = __import__("sqlalchemy").Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = __import__("sqlalchemy").Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    section_traces = relationship("SectionTrace", back_populates="artifact", cascade="all, delete-orphan")


class SectionTrace(Base):
    __tablename__ = "bw_section_traces"

    id = __import__("sqlalchemy").Column(Integer, primary_key=True, index=True)
    artifact_id = __import__("sqlalchemy").Column(Integer, ForeignKey("bw_planning_artifacts.id"), nullable=False, index=True)
    section_key = __import__("sqlalchemy").Column(String(100), nullable=False)
    source_phrases_json = __import__("sqlalchemy").Column(Text, default="[]", nullable=False)
    assumptions_json = __import__("sqlalchemy").Column(Text, default="[]", nullable=False)
    confidence = __import__("sqlalchemy").Column(String(20), default="medium", nullable=False)

    artifact = relationship("PlanningArtifact", back_populates="section_traces")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_demo_data() -> None:
    db = Session(engine)
    try:
        existing = db.query(PlanningArtifact).count()
        if existing > 0:
            return

        seeds = [
            {
                "title": "AI meal planner for busy parents",
                "raw_input": "Need quick weekly meals, kid-friendly, auto grocery list, budget cap $140/week, 30-min prep max.",
                "preferences": {"audience": "busy parents", "budget": "$140/week", "timeline": "MVP in 6 weeks"},
                "summary": "A family-first planning assistant that transforms time-poor meal chaos into reliable weekly plans and synced grocery runs.",
                "items": [
                    "Problem: parents juggle nutrition, cost, and time under daily stress",
                    "Users: dual-income households with young children",
                    "Solution: personalized weekly plan + grocery sync + leftovers routing",
                    "Differentiator: fast setup and kid-acceptance feedback loop",
                ],
                "score": 82,
                "score_rationale": "Strong recurring pain and clear monetization via premium planning tiers.",
            },
            {
                "title": "Freelance scope drift tracker",
                "raw_input": "I keep losing margin when client requests snowball. Need a way to detect drift from original scope and suggest renegotiation points.",
                "preferences": {"audience": "freelancers", "market_focus": "design + dev", "timeline": "8-week pilot"},
                "summary": "A scope control copilot that maps incoming requests to signed scope and highlights risk before margins erode.",
                "items": [
                    "Problem: hidden scope growth destroys profitability",
                    "Users: solo freelancers and boutique studios",
                    "Solution: request-to-scope diffing with risk flags",
                    "Differentiator: negotiation-ready language and evidence timeline",
                ],
                "score": 76,
                "score_rationale": "Niche but painful use case with high willingness to pay among independents.",
            },
        ]

        for s in seeds:
            artifact = PlanningArtifact(
                title=s["title"],
                raw_input=s["raw_input"],
                preferences_json=json.dumps(s["preferences"]),
                summary=s["summary"],
                items_json=json.dumps(s["items"]),
                score=s["score"],
                score_rationale=s["score_rationale"],
                is_seed=True,
            )
            db.add(artifact)
            db.flush()

            traces = [
                SectionTrace(
                    artifact_id=artifact.id,
                    section_key="problem",
                    source_phrases_json=json.dumps([s["raw_input"].split(".")[0]]),
                    assumptions_json=json.dumps(["Assumes recurring weekly behavior and repeat usage."]),
                    confidence="high",
                ),
                SectionTrace(
                    artifact_id=artifact.id,
                    section_key="solution",
                    source_phrases_json=json.dumps([s["raw_input"]]),
                    assumptions_json=json.dumps(["Assumes users accept lightweight onboarding."]),
                    confidence="medium",
                ),
            ]
            db.add_all(traces)

        db.commit()
    finally:
        db.close()

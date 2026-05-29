"""
AI Process - 자소서 첨삭 AI FastAPI 서버
포트 8001에서 실행
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.advisor import advise
from app.search import retrieve

app = FastAPI(title="자소서AI - AI Process", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AdviseRequest(BaseModel):
    draft: str
    question: str
    company: str
    n_refs: int = 3
    min_similarity: float = 0.5


class RetrieveRequest(BaseModel):
    query: str
    company: str | None = None
    org_type: str | None = None
    question_type: str | None = None
    n_results: int = 5


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/advise")
async def advise_endpoint(req: AdviseRequest):
    import asyncio
    result = await asyncio.to_thread(
        advise,
        draft=req.draft,
        question=req.question,
        company=req.company,
        n_refs=req.n_refs,
        min_similarity=req.min_similarity,
    )
    return result


@app.post("/retrieve")
async def retrieve_endpoint(req: RetrieveRequest):
    import asyncio
    results = await asyncio.to_thread(
        retrieve,
        req.query,
        company=req.company,
        org_type=req.org_type,
        question_type=req.question_type,
        n_results=req.n_results,
    )
    return {"results": results}

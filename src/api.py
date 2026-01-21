from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import tempfile
import os

# Import NLP modules
from src.nlp.timeline_extractor import TimelineExtractor
from src.nlp.financial_parser import FinancialParser
from src.nlp.relation_extractor import RelationExtractor
from src.nlp.case_classifier import CaseClassifier
from src.nlp.summarizer import Summarizer
from src.nlp.qa_engine import QAEngine
from src.parser import extract_metadata

app = FastAPI(
    title="ELIS - EPFO Legal Intelligence API",
    description="REST API for extracting information from EPF case documents",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize extractors (lazy load in production)
timeline_extractor = TimelineExtractor()
financial_parser = FinancialParser()
relation_extractor = RelationExtractor()
case_classifier = CaseClassifier()
summarizer = Summarizer()
qa_engine = QAEngine()

# Pydantic Models
class TextInput(BaseModel):
    text: str

class QARequest(BaseModel):
    question: str
    context: str

class MetadataResponse(BaseModel):
    date: Optional[str]
    id: Optional[str]

class ClassificationResponse(BaseModel):
    case_type: str
    outcome: str
    confidence: float

class TimelineEvent(BaseModel):
    date: str
    appeared: List[str]
    discussion: str
    outcome: str
    next_date: Optional[str]

class SummaryResponse(BaseModel):
    key_phrases: List[tuple]
    summary: str

# Endpoints
@app.get("/")
async def root():
    return {"message": "ELIS API v1.0.0", "docs": "/docs"}

@app.post("/extract/metadata", response_model=MetadataResponse)
async def extract_metadata_endpoint(input: TextInput):
    """Extract case metadata (date, ID) from text."""
    result = extract_metadata(input.text)
    return result

@app.post("/extract/timeline")
async def extract_timeline_endpoint(input: TextInput):
    """Extract chronological hearing events."""
    timeline = timeline_extractor.extract(input.text)
    return {"timeline": timeline, "count": len(timeline)}

@app.post("/extract/financial")
async def extract_financial_endpoint(input: TextInput):
    """Extract financial details from text."""
    result = financial_parser.extract_from_text(input.text)
    return result

@app.post("/extract/relations")
async def extract_relations_endpoint(input: TextInput):
    """Extract cause-effect relations."""
    relations = relation_extractor.extract(input.text)
    compliance = relation_extractor.extract_compliance_gaps(input.text)
    return {"relations": relations, "compliance_gaps": compliance}

@app.post("/classify", response_model=ClassificationResponse)
async def classify_case_endpoint(input: TextInput):
    """Classify case type (7A/14B) and compliance outcome."""
    result = case_classifier.classify(input.text)
    return result

@app.post("/summarize")
async def summarize_endpoint(input: TextInput):
    """Generate summary and key phrases."""
    key_phrases = summarizer.extract_key_phrases(input.text, top_n=10)
    summary = summarizer.summarize_extractive(input.text, num_sentences=5)
    return {"key_phrases": key_phrases, "summary": summary}

@app.post("/qa")
async def qa_endpoint(request: QARequest):
    """Answer a question based on context."""
    answer = qa_engine.answer(request.question, request.context)
    return {"question": request.question, "answer": answer}

@app.post("/extract/all")
async def extract_all_endpoint(input: TextInput):
    """Extract all information from text in one call."""
    return {
        "metadata": extract_metadata(input.text),
        "classification": case_classifier.classify(input.text),
        "timeline": timeline_extractor.extract(input.text),
        "financial": financial_parser.extract_from_text(input.text),
        "relations": relation_extractor.extract(input.text),
        "key_phrases": summarizer.extract_key_phrases(input.text, top_n=5),
        "summary": summarizer.summarize_extractive(input.text, num_sentences=3),
    }

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

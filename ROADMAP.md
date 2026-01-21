# EPF Case Extraction - Project Roadmap

## Current Progress (Phases 1-3 Partial)
- [x] Project Setup
- [x] PDF Text Extraction (OCR)
- [x] Data Schema (SQLite)
- [x] Rule-Based Extraction (Regex)
- [x] Table Extraction (tabula-py)
- [x] Basic NER (BERT)
- [x] Custom NER (GLiNER: Judge, Amount, Date)
- [x] Web Interface (Streamlit)
- [x] Date Validation

---

## Feature Extraction Phases (Completed)

### Phase 11: Timeline Extraction ✅
- [x] Extract hearing sequence from documents
- [x] Identify adjournment reasons
- [x] Build chronological event graph

### Phase 12: Financial Table Parsing ✅
- [x] Parse Schedule tables (account-wise dues)
- [x] Extract EE/ER shares, admin charges
- [x] Validate total = sum of breakdown

### Phase 13: Relation Extraction ✅
- [x] Extract cause-effect relationships
- [x] Map "employer failed to submit X"
- [x] Identify officer requests and outcomes

### Phase 14: Case Classification ✅
- [x] Classify 7A vs 14B orders
- [x] Identify compliance outcome

### Phase 15: Summarization ✅
- [x] Key phrase extraction (KeyBERT)
- [x] Extractive summarization

### Phase 16: QA System ✅
- [x] Answer: "What was total dues?"
- [x] Answer: "How many hearings?"

### Phase 17: Semantic Search ✅
- [x] Vector embeddings (sentence-transformers)
- [x] FAISS similarity search

---

---

## Evaluation & Deployment Phases (Completed)

### Phase 18: Test Suite ✅
- [x] 58 tests across 17 test files
- [x] All tests passing

### Phase 19: API Development ✅
- [x] FastAPI endpoints
- [x] Response time < 2s

### Phase 20: Documentation ✅
- [x] README with quick start
- [x] API documentation at /docs
- [x] Reproducible setup

---

## Success Criteria
- Extract structured fields: >90% accuracy
- Timeline reconstruction: Complete
- Financial dues: 100% accuracy
- QA system: >70% EM
- Process time: <30s per document

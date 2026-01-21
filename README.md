# ELIS - EPFO Legal Intelligence System

An end-to-end NLP system to extract structured and unstructured information from EPF legal case documents (7A and 14B orders).

## Features

- **OCR Pipeline**: Convert scanned PDFs to text using Tesseract
- **Metadata Extraction**: Case ID, Order Date, PF Code
- **Named Entity Recognition**: BERT + GLiNER for Judge, Establishment, Amount, Date
- **Timeline Extraction**: Chronological hearing events
- **Financial Parsing**: Schedule table parsing (EE/ER shares, admin charges)
- **Relation Extraction**: Officer directives, employer failures, consequences
- **Case Classification**: 7A vs 14B, compliance outcome
- **Summarization**: Key phrase extraction (KeyBERT), extractive summary
- **QA System**: Answer domain questions (total dues, hearings count)
- **Semantic Search**: FAISS + sentence-transformers similarity search
- **REST API**: FastAPI endpoints for all extraction tasks
- **Dashboard**: Streamlit UI for visualization

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Run Dashboard

```bash
streamlit run src/app.py
```

### Run API Server

```bash
uvicorn src.api:app --reload
```

API docs available at: http://localhost:8000/docs

### Run Tests

```bash
pytest tests/ -v
```

## Project Structure

```
pf-knowledge/
├── src/
│   ├── api.py              # FastAPI REST API
│   ├── app.py              # Streamlit Dashboard
│   ├── pipeline.py         # Main ETL pipeline
│   ├── loader.py           # PDF to image conversion
│   ├── ocr_engine.py       # Tesseract OCR
│   ├── parser.py           # Regex metadata extraction
│   ├── table_extractor.py  # Tabula table extraction
│   ├── database.py         # SQLAlchemy models
│   └── nlp/
│       ├── timeline_extractor.py   # Hearing timeline
│       ├── financial_parser.py     # Schedule tables
│       ├── relation_extractor.py   # Cause-effect relations
│       ├── case_classifier.py      # 7A/14B classification
│       ├── summarizer.py           # KeyBERT + extractive
│       ├── qa_engine.py            # Question answering
│       ├── semantic_search.py      # FAISS search
│       ├── entity_extractor.py     # GLiNER NER
│       └── ner_engine.py           # BERT NER
├── tests/                  # Pytest test suite
├── case_pdfs/              # Sample PDF documents
├── ROADMAP.md              # Project roadmap
└── requirements.txt        # Dependencies
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/extract/metadata` | POST | Extract case ID and date |
| `/extract/timeline` | POST | Extract hearing timeline |
| `/extract/financial` | POST | Extract financial details |
| `/extract/relations` | POST | Extract cause-effect relations |
| `/classify` | POST | Classify case type |
| `/summarize` | POST | Generate summary |
| `/qa` | POST | Answer questions |
| `/extract/all` | POST | Full extraction |

## Test Coverage

- 58 tests across 17 test files
- Covers: OCR, parsing, NER, timeline, financial, relations, classification, QA, API

## License

MIT

# SETTribe Chatbot Diagnostic Report

## Incident

The chatbot initially showed no welcome message and returned the same response for different questions. The backend logs also contained Uvicorn command errors and LangChain warnings.

## Confirmed Root Causes

1. The frontend originally used a hard-coded placeholder response instead of calling the API.
2. The frontend did not add an initial assistant welcome message.
3. The backend had no `LLM_API_KEY`, so it used `FakeListLLM`, which always returned one fixed sentence.
4. Without an LLM key, the classifier returned `UNKNOWN` for normal course questions.
5. The local Chroma index contained course data, but the response pipeline discarded it behind the fixed fake LLM response.
6. The command `--reaload` was misspelled. The correct option is `--reload`.

## Fixes Applied

- `frontend/js/chatbot.js` now calls `POST http://127.0.0.1:8000/api/chat/`.
- The frontend now creates a session ID and displays a welcome message on load.
- `backend/app/api/chat.py` handles greetings locally and records them as `GENERAL_FAQ`.
- `backend/app/chatbot/classifier.py` uses safe keyword classification when no LLM key exists.
- `backend/app/rag/chains.py` returns retrieved approved documents when no LLM key exists instead of returning a fixed mock response.

## Verification Results

### Greeting

Input: `hi`

Result: HTTP 200, `GENERAL_FAQ`, and a welcome response.

### Course question

Input: `What courses are available?`

Result: HTTP 200, `COURSE_ENQUIRY`, and the indexed Data Analytics document.

The current knowledge base contains one course document: Data Analytics.

## Remaining Flaws and Risks

### Knowledge coverage

Only one course document was found. Questions about other courses, locations, internships, policies, or company information may not have enough approved content.

### LLM configuration

Without `LLM_API_KEY`, the fallback returns retrieved document text rather than a conversational LLM answer. This is safe but less polished.

### Source response

Retrieved source metadata is currently not returned in the API `sources` field, even though the answer includes a source label.

### Retrieval quality

The fallback uses fake embeddings when no API key exists. This is acceptable for a single local document but is not reliable for a larger knowledge base.

### Ingestion support

The loader currently handles TXT files only. PDF, DOCX, HTML, Markdown, JSON, and CSV support is not implemented yet.

### Security

The API currently allows all CORS origins and the admin routes have no authentication. These settings are unsuitable for production.

### API performance

The RAG chain and vector store are created during each chat request. They should be initialized once and reused in production.

### Dependency warnings

Chroma and `RunnableWithMessageHistory` emit deprecation warnings. They do not currently prevent startup, but both should be migrated before upgrading LangChain further.

## Correct Startup Commands

Backend:

```powershell
cd "C:\Users\Rahul soni\Chatbotsettribe\backend"
python -m uvicorn app.main:app --reload
```

Frontend:

Serve the `frontend` directory with Live Server and open its generated URL. Do not open a different old copy of `index.html`.

## Production Setup Still Required

Create `backend/.env` with an actual provider key before expecting natural-language LLM responses:

```env
LLM_API_KEY=your_actual_key
```

Never put this key in frontend JavaScript or commit the `.env` file.

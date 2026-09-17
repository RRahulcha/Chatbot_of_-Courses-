# PROJECT: SETTRIBE AI STUDENT & CAREER ASSISTANT

Build a production-ready AI chatbot for the SETTribe website.

The chatbot must act as an intelligent Student, Course, Internship and Career Assistant for SETTribe.

The primary objective is to help college students, graduates, job seekers and prospective students quickly understand SETTribe courses, internships, training programs, fees/costs, eligibility, online/offline learning, locations, contact information, career support and other official SETTribe information.

The chatbot must use:

* Python
* FastAPI
* LangChain
* RAG (Retrieval-Augmented Generation)
* LLM
* Embeddings
* Vector Database
* Prompt Engineering
* Conversation Memory
* Document loaders
* Retrieval pipeline
* REST APIs
* HTML
* CSS
* JavaScript
* Secure backend architecture

The system should be designed so the LLM does NOT independently invent SETTribe information.

---

# 1. MAIN OBJECTIVE

Create an AI-powered chatbot that can answer questions such as:

* What courses does SETTribe offer?
* Which course is suitable for me?
* What is the duration of this course?
* What is the course fee?
* Is the course available online?
* Is the course available offline?
* Where is the offline training center?
* How can I apply?
* What are the eligibility requirements?
* Do you provide internships?
* What type of internship is available?
* Do students work on real projects?
* Is placement assistance available?
* Do you provide interview preparation?
* Do you help with resumes and LinkedIn?
* What technologies are covered?
* Can a graduate join?
* Can a final-year student join?
* How can I contact SETTribe?
* Where is SETTribe located?
* How can I submit an enquiry?
* Can I speak with a career advisor?
* What programs are available?
* What is SETTribe's contribution to society?
* What does SETTribe do?
* What is STEP by SETTribe?
* What is the difference between online and offline training?

The chatbot must provide concise, accurate and useful answers.

---

# 2. IMPORTANT RULE: RAG-FIRST KNOWLEDGE SYSTEM

The chatbot must use RAG as the primary knowledge mechanism.

Do NOT allow the LLM to freely hallucinate SETTribe-specific information.

The flow should be:

USER QUESTION
↓
CHATBOT
↓
QUERY UNDERSTANDING
↓
QUERY CLASSIFICATION
↓
RETRIEVAL FROM SETTRIBE KNOWLEDGE BASE
↓
RELEVANT DOCUMENTS / CHUNKS
↓
CONTEXT + USER QUESTION
↓
LANGCHAIN PROMPT
↓
LLM
↓
FACTUAL ANSWER
↓
OPTIONAL SOURCE / REFERENCE
↓
USER

The chatbot should answer SETTribe-specific questions primarily from retrieved documents.

---

# 3. KNOWLEDGE BASE

Create a structured knowledge base containing approved SETTribe information.

The knowledge base should contain:

## Company Information

* About SETTribe
* Mission
* Vision
* Company history
* Technology services
* Social contribution
* Education initiatives
* Employability initiatives
* E-Governance work
* Digital transformation work
* Company achievements
* Awards
* Clients
* Projects

## STEP Information

* STEP by SETTribe
* Skill Transition & Employability Program
* Campus-to-corporate model
* Learning methodology
* Industry exposure
* Mentorship
* Career preparation
* Placement assistance
* Real-world projects
* Interview preparation

## Course Information

For every course create structured metadata:

course_name
category
description
duration
mode
online_available
offline_available
location
eligibility
skills
technologies
curriculum
projects
internship
placement_assistance
fees
discount
certificate
career_outcomes
application_process
contact_information

## Internship Information

Store:

* Internship programs
* Internship domains
* Technologies
* Duration
* Eligibility
* Internship process
* Project experience
* Mentorship
* Certificate information
* Career benefits
* Placement/career assistance

## Admission Information

Store:

* Eligibility
* Registration process
* Application process
* Required information
* Selection process
* Onboarding process
* Batch information
* Schedule
* Contact procedure

## Fees

Store:

* Course fees
* Internship fees if applicable
* Discounts
* Offers
* Payment information
* Installment information

IMPORTANT:

If fee information is unavailable or has changed, NEVER invent a fee.

Instead say:

"I don't have the latest fee information in my knowledge base. I can help you submit an enquiry to the SETTribe team."

Then offer the enquiry workflow.

## Location

Store:

* SETTribe office locations
* Training centers
* Development centers
* Address
* Contact number
* Email
* Working hours
* Map information if officially available

---

# 4. DATA SOURCES

The knowledge base should support multiple sources:

1. SETTribe official website
2. STEP website
3. Course pages
4. Internship pages
5. FAQ pages
6. Contact page
7. Admission information
8. Official PDFs
9. Official brochures
10. Course curriculum documents
11. Internal approved documents
12. Structured JSON/YAML course data

The system should allow administrators to update documents without changing the chatbot code.

---

# 5. DOCUMENT INGESTION PIPELINE

Create a separate ingestion pipeline.

Workflow:

DOCUMENTS
↓
Document Loader
↓
Text Extraction
↓
Cleaning
↓
Metadata Extraction
↓
Chunking
↓
Embedding Model
↓
Vector Database
↓
Retriever

Support:

* PDF
* HTML
* TXT
* DOCX
* Markdown
* JSON
* CSV

Every chunk should contain metadata such as:

source
url
page
document_type
course_name
category
last_updated

Example:

{
"course_name": "Data Analytics",
"category": "Course",
"source": "SETTribe official website",
"url": "...",
"last_updated": "YYYY-MM-DD"
}

---

# 6. VECTOR DATABASE

Use a vector database for semantic retrieval.

The architecture should allow:

* Chroma for local development
* FAISS as an alternative
* Pinecone/Qdrant/Weaviate as production options

Make the vector database configurable through environment variables.

Do not hard-code API keys.

Use:

.env

Example:

LLM_API_KEY=
VECTOR_DB_URL=
EMBEDDING_MODEL=
DATABASE_URL=

---

# 7. LANGCHAIN PIPELINE

Build the chatbot using LangChain.

Recommended pipeline:

User Input
↓
Input Validation
↓
Conversation Context
↓
Query Classification
↓
Query Rewriting
↓
Retriever
↓
Relevant Context
↓
Prompt Template
↓
LLM
↓
Response Validation
↓
Final Response

Create separate modules for:

* LLM initialization
* Embeddings
* Document loading
* Text splitting
* Vector store
* Retriever
* Prompt templates
* Conversation memory
* Query classification
* Response generation
* Lead capture
* Human handoff

---

# 8. QUERY CLASSIFICATION

Before retrieval, classify the user's question.

Categories:

1. COURSE_ENQUIRY
2. COURSE_FEE
3. COURSE_ELIGIBILITY
4. COURSE_DURATION
5. ONLINE_OFFLINE
6. INTERNSHIP
7. ADMISSION
8. PLACEMENT
9. CAREER_SUPPORT
10. COMPANY_INFORMATION
11. LOCATION
12. CONTACT
13. SOCIAL_IMPACT
14. TECHNICAL_COURSE_DOUBT
15. COURSE_RECOMMENDATION
16. GENERAL_FAQ
17. ENQUIRY_REQUEST
18. HUMAN_SUPPORT
19. UNKNOWN

Example:

User:
"I am a B.Tech graduate and want to learn Python. Which SETTribe course should I take?"

Classification:

COURSE_RECOMMENDATION

Then retrieve relevant courses.

---

# 9. COURSE RECOMMENDATION ENGINE

The chatbot should intelligently recommend courses.

Ask only necessary questions:

* Education/background
* Current skill level
* Career goal
* Preferred technology
* Online/offline preference
* Location
* Available time

Example:

User:
"I don't know which course to choose."

Bot:

"Sure. I can help you choose the right SETTribe program. What is your main goal?"

Options:

1. Get a software development job
2. Become a Data Analyst
3. Learn AI/ML
4. Become a Tester/SDET
5. Learn Web Development
6. Get an internship
7. I'm not sure

The recommendation must be based on actual SETTribe course data.

Do not invent courses.

---

# 10. STUDENT DOUBT SOLVING

The chatbot should support educational questions related to SETTribe courses.

For example:

Student:

"What is Selenium?"

The chatbot can provide a general educational explanation.

But if the question is:

"Does SETTribe's SDET course teach Selenium?"

The answer must come from RAG.

The system should distinguish between:

GENERAL EDUCATIONAL QUESTION

and

SETTRIBE-SPECIFIC QUESTION.

---

# 11. COST / FEE ENQUIRY

The chatbot must make fee enquiries extremely easy.

Example:

User:
"How much does the Data Analytics course cost?"

If fee exists:

"According to the latest SETTribe information, the course fee is ₹X."

Then:

"Would you like to submit an enquiry?"

Buttons:

[Submit Enquiry]
[Talk to Career Advisor]

If fee does not exist:

"I don't have the latest fee information available. I can help you send an enquiry to the SETTribe team."

Then collect:

Name
Phone
Email
Course
Qualification
Message

---

# 12. LEAD / ENQUIRY WORKFLOW

Create a conversational enquiry system.

Workflow:

USER
↓
CHATBOT
↓
IDENTIFY INTEREST
↓
ASK REQUIRED DETAILS
↓
NAME
↓
PHONE
↓
EMAIL
↓
QUALIFICATION
↓
COURSE
↓
ONLINE/OFFLINE PREFERENCE
↓
MESSAGE
↓
CONFIRM INFORMATION
↓
SUBMIT ENQUIRY
↓
DATABASE
↓
ADMIN / COUNSELOR
↓
FOLLOW-UP

Do not ask for all fields at once.

Collect information naturally through conversation.

Example:

Bot:
"Which course are you interested in?"

User:
"Data Analytics."

Bot:
"Great. Are you currently a student or a graduate?"

Continue only with useful questions.

---

# 13. HUMAN HANDOFF

The chatbot must know when it cannot solve the problem.

Trigger human handoff when:

* User explicitly requests a person
* Fee is unavailable
* User asks about special discounts
* User asks for customized pricing
* User has a complaint
* User has a complicated admission issue
* User asks about an individual application
* The retrieved information is insufficient
* The chatbot has low confidence
* The question requires private student information

Response:

"I want to make sure you get accurate information. This question is better handled by a SETTribe career advisor."

Then provide:

[Talk to Career Advisor]
[Submit Enquiry]
[Contact SETTribe]

---

# 14. HALLUCINATION PREVENTION

Implement strict grounding.

SYSTEM RULE:

"You are SETTribe's official AI Student & Career Assistant. Answer SETTribe-specific questions only using the information retrieved from the approved SETTribe knowledge base. Never invent course names, fees, discounts, locations, schedules, placement statistics, internship guarantees, salaries, or company information."

If information is unavailable:

"I couldn't find that information in the current SETTribe knowledge base."

Then suggest contacting SETTribe.

Never guess.

---

# 15. SOURCE ATTRIBUTION

Whenever possible, show where the answer came from.

Example:

"According to the SETTribe course information..."

Source:
SETTribe → Course Page

Add a small:

"Source"

link beneath the response.

This improves trust and allows students to verify information.

---

# 16. MULTI-TURN MEMORY

The chatbot should remember relevant conversation context during the current session.

Example:

User:
"I want a Data Analytics course."

Bot:
"Are you a student or graduate?"

User:
"Graduate."

Bot:
"What is your current experience with SQL?"

The chatbot should remember:

course_interest = Data Analytics
qualification = Graduate

Do not repeatedly ask the same questions.

Use session-based conversation memory.

---

# 17. MULTILINGUAL SUPPORT

The chatbot should support:

* English
* Hindi
* Marathi

Example:

User:
"Data Analytics course ki fees kitni hai?"

Respond naturally in Hindi.

User:
"Data Analytics course chi fees kiti aahe?"

Respond naturally in Marathi.

Maintain the same factual grounding regardless of language.

---

# 18. CHATBOT UI

Create a modern professional chatbot widget for the SETTribe website.

The chatbot should contain:

Header:

"SETTribe AI Assistant"

Subtitle:

"Ask about courses, internships & careers"

Features:

* Chat messages
* User/bot avatars
* Typing indicator
* Suggested questions
* Quick action buttons
* Source links
* Enquiry form
* Contact advisor button
* Clear conversation button
* Mobile responsive interface

Suggested questions:

"Which course is right for me?"
"What courses are available?"
"What are the course fees?"
"Do you offer internships?"
"Online or offline?"
"Where is SETTribe located?"
"How can I contact SETTribe?"

---

# 19. QUICK ACTION MENU

Create buttons:

🎓 Courses

💰 Fees

💼 Internships

📚 Course Details

🏢 About SETTribe

📍 Locations

📞 Contact

📝 Submit Enquiry

👨‍💼 Talk to Career Advisor

---

# 20. ADMIN DASHBOARD

Create an admin dashboard.

Admin should be able to:

* Upload documents
* Delete documents
* Update documents
* Add courses
* Update fees
* Update course availability
* Update locations
* Update contact details
* Rebuild vector index
* View conversations
* View enquiries
* View unanswered questions
* View frequently asked questions
* View chatbot analytics

Dashboard metrics:

* Total conversations
* Total users
* Total enquiries
* Course enquiries
* Internship enquiries
* Fee enquiries
* Human handoffs
* Unanswered questions
* Most asked questions
* Most requested courses

---

# 21. ANALYTICS

Track:

conversation_id
session_id
timestamp
question
intent
course
response
retrieved_documents
confidence
lead_created
human_handoff

Create analytics such as:

"Top 10 questions students ask"

"Most requested course"

"Most common enquiry"

"Questions chatbot could not answer"

This information should help SETTribe improve its website and course information.

---

# 22. SECURITY

Implement:

* Environment variables
* API key protection
* Input validation
* Rate limiting
* CORS configuration
* Secure API endpoints
* SQL injection protection
* XSS protection
* Authentication for admin
* Secure database access

Never expose LLM API keys in frontend JavaScript.

---

# 23. DATABASE

Use a database to store:

Users
Sessions
Messages
Enquiries
Courses
Documents
Feedback
Analytics

Example tables:

users
courses
documents
chat_sessions
chat_messages
enquiries
feedback
admin_users

---

# 24. FEEDBACK SYSTEM

After useful interactions:

"Was this answer helpful?"

Buttons:

👍 Yes
👎 No

If No:

"What were you looking for?"

Store the feedback for improvement.

---

# 25. UNKNOWN QUESTION HANDLING

If the user asks:

"Who will win the IPL?"

The bot should not pretend it is a SETTribe expert.

Reply:

"I'm primarily here to help with SETTribe courses, internships, training and career-related enquiries. I can help you with those topics."

---

# 26. COURSE COMPARISON

Allow students to compare courses.

Example:

User:

"Compare Data Analytics and Data Science."

Return:

Course
Skills
Technologies
Duration
Mode
Projects
Career direction
Internship
Placement assistance
Fee, if available

Only use verified SETTribe data.

---

# 27. ONLINE VS OFFLINE

The chatbot must clearly answer:

* Which courses are online?
* Which courses are offline?
* Offline location
* Online learning process
* Schedule
* Availability
* Difference between online/offline

If information is not available:

Do not guess.

Offer an enquiry.

---

# 28. SOCIAL CONTRIBUTION

Create a dedicated knowledge category:

"SETTribe Social Impact"

The chatbot should explain verified information about:

* Education
* Employability
* Skill development
* E-Governance
* Public service initiatives
* Technology for society
* Student career development
* Campus-to-corporate initiatives

Only use information from official sources.

---

# 29. RESPONSE STYLE

The chatbot should be:

* Professional
* Friendly
* Student-friendly
* Clear
* Concise
* Helpful
* Encouraging
* Non-robotic

Avoid:

* Extremely long responses
* Unnecessary technical jargon
* Fake claims
* Unsupported statistics
* False guarantees
* Repeated information

Use bullets and short sections.

---

# 30. SAMPLE RESPONSE

User:

"Hi, I am a final-year B.Tech student. I want to learn software testing. What do you recommend?"

Bot:

"Absolutely. I can help you explore SETTribe's testing-focused programs.

Based on your interest in software testing, you may want to explore the SDET/Software Testing program.

It focuses on areas such as:

• Software Testing
• Automation Testing
• Java
• SQL
• Selenium
• Agile methodologies
• Real-world projects

The program also includes practical learning and career support.

Would you like to know:

[Course Curriculum]
[Eligibility]
[Fees]
[Internship]
[Submit Enquiry]"

IMPORTANT:

The exact answer must be generated from the current RAG knowledge base.

---

# 31. PROJECT ARCHITECTURE

Use this architecture:

```
                SETTRIBE WEBSITE
                       |
                       ↓
                CHATBOT FRONTEND
                HTML/CSS/JS
                       |
                       ↓
                   FASTAPI
                       |
            ┌──────────┴──────────┐
            ↓                     ↓
    Query Classifier         Session Memory
            |
            ↓
      LangChain Pipeline
            |
            ↓
      Query Rewriting
            |
            ↓
         Retriever
            |
            ↓
      Vector Database
            |
            ↓
    Relevant SETTribe Docs
            |
            ↓
     Prompt Construction
            |
            ↓
            LLM
            |
            ↓
   Response Validation
            |
    ┌───────┴────────┐
    ↓                ↓
Answer           Human Handoff
    |
    ↓
User Interface
```

DOCUMENT INGESTION:

SETTRIBE WEBSITE / PDF / DOCS
↓
Document Loader
↓
Text Cleaning
↓
Chunking
↓
Embeddings
↓
Vector Database
↓
Retriever

---

# 32. RECOMMENDED PROJECT STRUCTURE

Create:

settribe-ai-chatbot/

```
backend/

    app/

        main.py

        config.py

        api/

            chat.py
            enquiry.py
            admin.py

        core/

            llm.py
            embeddings.py
            security.py

        rag/

            loaders.py
            splitter.py
            vectorstore.py
            retriever.py
            prompts.py
            chains.py

        chatbot/

            classifier.py
            memory.py
            response.py
            guardrails.py

        database/

            models.py
            database.py

        services/

            enquiry_service.py
            analytics_service.py

    ingestion/

        ingest_documents.py
        update_vectors.py

    requirements.txt
    .env.example

frontend/

    index.html

    css/

        chatbot.css

    js/

        chatbot.js
        api.js
        ui.js

admin/

    index.html
    css/
    js/

data/

    courses/
    faq/
    company/
    internships/
    policies/

tests/

    test_rag.py
    test_chatbot.py
    test_enquiry.py

README.md
```

---

# 33. API ENDPOINTS

Create:

POST /api/chat

POST /api/enquiry

GET /api/courses

GET /api/courses/{course_id}

GET /api/contact

POST /api/feedback

POST /api/admin/documents

DELETE /api/admin/documents/{id}

POST /api/admin/reindex

GET /api/admin/analytics

GET /api/admin/enquiries

---

# 34. CHAT API RESPONSE

Return structured JSON:

{
"answer": "...",
"intent": "COURSE_ENQUIRY",
"sources": [],
"suggested_actions": [
"View Course",
"Check Fees",
"Submit Enquiry"
],
"requires_human": false
}

---

# 35. RAG QUALITY REQUIREMENTS

Implement:

* Semantic search
* Metadata filtering
* Top-K retrieval
* Similarity threshold
* Context compression if necessary
* Query rewriting
* Source attribution
* Context-aware responses

If retrieval confidence is below the configured threshold:

Do NOT answer with an invented response.

Use:

"I couldn't find enough verified information to answer that accurately."

Then provide a contact/enquiry option.

---

# 36. TESTING

Create test cases for:

1. Course question
2. Fee question
3. Internship question
4. Eligibility question
5. Location question
6. Contact question
7. Online/offline question
8. Company question
9. Social contribution question
10. Course recommendation
11. Unknown question
12. Hallucination attempt
13. Human handoff
14. Enquiry creation
15. Multi-turn conversation
16. Hindi question
17. Marathi question
18. Typographical errors
19. Ambiguous course query
20. Outdated information

---

# 37. IMPORTANT BUSINESS RULES

The chatbot must NEVER:

* Guarantee a job
* Guarantee placement
* Invent salary figures
* Invent fees
* Invent discounts
* Invent course names
* Invent batch dates
* Invent internship availability
* Invent company partnerships
* Invent certifications
* Reveal private student information
* Give unsupported SETTribe claims

The chatbot SHOULD:

* Answer verified questions
* Recommend relevant programs
* Explain courses
* Help students understand options
* Collect enquiries
* Connect students with advisors
* Provide official source references
* Escalate uncertain questions
* Learn from unanswered questions through analytics

---

# 38. FINAL USER EXPERIENCE

The student should be able to go from:

"I have no idea what course to take"

to:

"Here is the recommended SETTribe program"

to:

"Here are the course details"

to:

"Here is the fee / enquiry option"

to:

"I want to join"

to:

"Here is my enquiry"

without leaving the chatbot.

The chatbot should effectively function as:

AI COURSE ADVISOR
+
AI FAQ ASSISTANT
+
AI INTERNSHIP ASSISTANT
+
AI ADMISSION ASSISTANT
+
AI CAREER ASSISTANT
+
AI ENQUIRY/LEAD GENERATOR

---

# 39. DEVELOPMENT APPROACH

Build the project in phases.

PHASE 1:
Basic chatbot UI + FastAPI

PHASE 2:
Document ingestion

PHASE 3:
Embeddings + Vector Database

PHASE 4:
LangChain RAG pipeline

PHASE 5:
LLM integration

PHASE 6:
Conversation memory

PHASE 7:
Course recommendation

PHASE 8:
Enquiry/lead workflow

PHASE 9:
Human handoff

PHASE 10:
Admin dashboard

PHASE 11:
Analytics

PHASE 12:
Security + testing

PHASE 13:
Production deployment

Do not attempt to create everything as one unstructured file.

Keep frontend, backend, RAG, database and admin functionality modular.

---

# 40. SUCCESS CRITERIA

The project is complete only when:

✓ Student can ask natural-language questions

✓ RAG retrieves relevant SETTribe information

✓ LangChain manages the retrieval/generation pipeline

✓ LLM generates natural responses

✓ Hallucinations are controlled

✓ Sources can be displayed

✓ Course information can be retrieved

✓ Fee enquiries work

✓ Internship enquiries work

✓ Online/offline information works

✓ Location/contact information works

✓ Course recommendation works

✓ Student enquiry can be submitted

✓ Human advisor handoff works

✓ Conversation context works

✓ Admin can update knowledge

✓ Analytics work

✓ Mobile UI works

✓ API keys are secure

✓ Backend and frontend are separated

✓ The system can be deployed to production

Build this as a real-world production-oriented AI chatbot rather than a simple ChatGPT clone.

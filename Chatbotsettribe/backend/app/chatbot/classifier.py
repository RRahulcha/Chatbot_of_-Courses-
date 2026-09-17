from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.core.llm import get_llm
from app.config import settings

CLASSIFIER_PROMPT = """
You are an expert intent classifier for the SETTribe Student & Career Assistant.
Classify the following user query into exactly one of these categories:
COURSE_ENQUIRY, COURSE_FEE, COURSE_ELIGIBILITY, COURSE_DURATION, ONLINE_OFFLINE, INTERNSHIP, ADMISSION, PLACEMENT, CAREER_SUPPORT, COMPANY_INFORMATION, LOCATION, CONTACT, SOCIAL_IMPACT, TECHNICAL_COURSE_DOUBT, COURSE_RECOMMENDATION, GENERAL_FAQ, ENQUIRY_REQUEST, HUMAN_SUPPORT, UNKNOWN.

Reply ONLY with the exact category name. Do not add any extra text or punctuation.

User query: {query}
Category:"""

def classify_query(query: str) -> str:
    if not settings.llm_api_key or settings.llm_api_key == "your_llm_api_key_here":
        normalized_query = query.lower()
        if any(word in normalized_query for word in ["course", "courses", "program", "training"]):
            if any(word in normalized_query for word in ["fee", "fees", "cost", "price"]):
                return "COURSE_FEE"
            return "COURSE_ENQUIRY"
        if any(word in normalized_query for word in ["internship", "intern"]):
            return "INTERNSHIP"
        if any(word in normalized_query for word in ["location", "where", "address"]):
            return "LOCATION"
        if any(word in normalized_query for word in ["contact", "phone", "email"]):
            return "CONTACT"
        return "UNKNOWN"

    llm = get_llm()
    prompt = PromptTemplate.from_template(CLASSIFIER_PROMPT)
    chain = prompt | llm | StrOutputParser()
    try:
        result = chain.invoke({"query": query}).strip()
        # Verify it falls into one of our predefined categories
        valid_categories = [
            "COURSE_ENQUIRY", "COURSE_FEE", "COURSE_ELIGIBILITY", "COURSE_DURATION", 
            "ONLINE_OFFLINE", "INTERNSHIP", "ADMISSION", "PLACEMENT", "CAREER_SUPPORT", 
            "COMPANY_INFORMATION", "LOCATION", "CONTACT", "SOCIAL_IMPACT", 
            "TECHNICAL_COURSE_DOUBT", "COURSE_RECOMMENDATION", "GENERAL_FAQ", 
            "ENQUIRY_REQUEST", "HUMAN_SUPPORT", "UNKNOWN"
        ]
        if result not in valid_categories:
            return "UNKNOWN"
        return result
    except Exception as e:
        print(f"Classification error: {e}")
        return "UNKNOWN"

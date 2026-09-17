from app.rag.vectorstore import get_vector_store

COURSE_KEYWORDS = [
    "course",
    "courses",
    "mern",
    "mern stack",
    ".net",
    "net fsd",
    "java fsd",
    "java full stack",
    "software testing",
    "cyber security",
    "data analysis",
    "data analytics",
    "data science",
    "devops",
    "web development",
    "mobile app",
]

def is_course_query(query: str) -> bool:
    """
    Detect whether the user's question is related to courses.
    """
    query_lower = query.lower().strip()

    return any(
        keyword in query_lower
        for keyword in COURSE_KEYWORDS
    )


def get_retriever(k=4):
    """
    Return a course-aware retriever for the SETTribe
    website knowledge base.

    Normal questions use standard similarity search.

    Course-related questions additionally retrieve the
    dedicated course_catalog documents so that official
    course names such as MERN Stack and .NET FSD are not
    hidden behind generic website chunks.

    """
    db = get_vector_store()
    class CourseAwareRetriever:
        def __init__(self, vector_store, top_k):
            self.vector_store = vector_store
            self.top_k = top_k

        def invoke(self, query, config=None):
            # Normal semantic retrieval
            documents = self.vector_store.similarity_search(
                query,
                k=self.top_k,
            )

            # For course questions, explicitly retrieve
            # the dedicated course catalog documents.
            if is_course_query(query):
                catalog_documents = (
                    self.vector_store.similarity_search(
                        query,
                        k=2,
                        filter={
                            "content_type": "course_catalog"
                        },
                    )
                )

                existing_contents = {
                    doc.page_content
                    for doc in documents
                }

                for document in catalog_documents:
                    if document.page_content not in existing_contents:
                        documents.append(document)

            return documents


    return CourseAwareRetriever(db, k)
    

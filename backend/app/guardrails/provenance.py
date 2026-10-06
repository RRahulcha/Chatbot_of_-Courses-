from app.core.llm import get_llm


def groq_provenance_llm(prompt: str) -> str:
    llm = get_llm()
    response = llm.invoke(prompt)

    content = getattr(response, "content", response)

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text_parts = []

        for item in content:
            if isinstance(item, dict):
                text = item.get("text")
                if text:
                    text_parts.append(str(text))
            elif isinstance(item, str):
                text_parts.append(item)

        return "\n".join(text_parts)

    return str(content)
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import OllamaLLM

embeddings = OllamaEmbeddings(
    model="nomic-embed-text"
)

vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings
)

retriever = vectorstore.as_retriever()

llm = OllamaLLM(model="phi3")

while True:
    question = input("\nAsk: ")

    if question == "exit":
        break

    docs = retriever.invoke(question)

    # REMOVE DUPLICATES
    seen = set()
    unique_docs = []

    for doc in docs:
        if doc.page_content not in seen:
            seen.add(doc.page_content)
            unique_docs.append(doc)

    context = "\n".join([
        doc.page_content for doc in unique_docs
    ])

    prompt = f"""
    You are an ecommerce AI assistant.

    Answer ONLY using product data below.

    Product Data:
    {context}

    Question:
    {question}
    """

    response = llm.invoke(prompt)

    print("\nAI:")
    print(response)
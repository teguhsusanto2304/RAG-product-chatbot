from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import OllamaLLM

# FASTAPI
app = FastAPI()

# ENABLE CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# EMBEDDINGS
embeddings = OllamaEmbeddings(
    model="nomic-embed-text"
)

# VECTOR STORE
vectorstore = Chroma(
    persist_directory="./../chroma_db",
    embedding_function=embeddings
)

# RETRIEVER
retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 3}
)

# LLM
llm = OllamaLLM(model="phi3")

# REQUEST MODEL
class ChatRequest(BaseModel):
    message: str

# CHAT ENDPOINT
@app.post("/chat")
async def chat(req: ChatRequest):

    question = req.message

    docs = retriever.invoke(question)

    # REMOVE DUPLICATES
    seen = set()
    unique_docs = []

    for doc in docs:
        if doc.page_content not in seen:
            seen.add(doc.page_content)
            unique_docs.append(doc)

    context = "\n".join([
        doc.page_content
        for doc in unique_docs
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

    return {
        "question": question,
        "answer": response
    }
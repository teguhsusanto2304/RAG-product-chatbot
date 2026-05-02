from langchain_ollama import OllamaLLM
from langchain_ollama import OllamaEmbeddings

from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader

# Load document
loader = TextLoader("docs/company.txt")
documents = loader.load()

# Split text
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

docs = text_splitter.split_documents(documents)

# Embedding model
embeddings = OllamaEmbeddings(
    model="nomic-embed-text"
)

# Store vectors
vectorstore = Chroma.from_documents(
    documents=docs,
    embedding=embeddings,
    persist_directory="./chroma_db"
)

# LLM
llm = OllamaLLM(model="llama3.1:8b")

# User question
question = "What is the refund policy?"

# Retrieve relevant docs
retriever = vectorstore.as_retriever()

retrieved_docs = retriever.invoke(question)

context = "\n".join([doc.page_content for doc in retrieved_docs])

# Prompt
prompt = f"""
Answer the question based ONLY on the context below.

Context:
{context}

Question:
{question}
"""

# Generate answer
response = llm.invoke(prompt)

print("\nAnswer:")
print(response)
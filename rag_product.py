from sqlalchemy import create_engine, text

from langchain.schema import Document
from langchain_community.vectorstores import Chroma

from langchain_ollama import OllamaEmbeddings
from langchain_ollama import OllamaLLM

# DATABASE
DATABASE_URL = "mysql+pymysql://root:@localhost/emp"

engine = create_engine(DATABASE_URL)

products = []

with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM products"))

    for row in result:
        content = f"""
        Product Name: {row.name}
        Category: {row.category}
        Description: {row.description}
        Price: ${row.price}
        Stock: {row.stock}
        """

        products.append(Document(page_content=content))

# EMBEDDINGS
embeddings = OllamaEmbeddings(
    model="nomic-embed-text"
)

# VECTOR STORE
vectorstore = Chroma.from_documents(
    documents=products,
    embedding=embeddings,
    persist_directory="./chroma_db"
)

retriever = vectorstore.as_retriever()

# LLM
llm = OllamaLLM(model="llama3.1:8b")

# CHAT LOOP
while True:
    question = input("\nAsk: ")

    if question == "exit":
        break

    docs = retriever.invoke(question)

    context = "\n".join([
        doc.page_content for doc in docs
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
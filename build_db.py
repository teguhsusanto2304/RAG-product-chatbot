from sqlalchemy import create_engine, text

from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings

DATABASE_URL = "mysql+pymysql://root:@localhost/emp"

engine = create_engine(DATABASE_URL)

products = []

with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM products"))

    for row in result:
        content = f"""
        Product ID: {row.id}
        Product Name: {row.name}
        Category: {row.category}
        Description: {row.description}
        Price: ${row.price}
        Stock: {row.stock}
        """

        products.append(
            Document(
                page_content=content,
                metadata={"id": row.id}
            )
        )

embeddings = OllamaEmbeddings(
    model="nomic-embed-text"
)

vectorstore = Chroma.from_documents(
    documents=products,
    embedding=embeddings,
    persist_directory="./chroma_db"
)

print("Vector DB created.")
import os
import chromadb
from chromadb.utils import embedding_functions
from pypdf import PdfReader

DATA_FOLDER = "data"

client = chromadb.PersistentClient(path="./rag_db")

collection = client.get_or_create_collection(
    name="pdf_chunks",
    embedding_function=embedding_functions.DefaultEmbeddingFunction()
)

def extract_text_from_pdfs():
    documents = []
    ids = []
    counter = 1

    for filename in os.listdir(DATA_FOLDER):

        if filename.endswith(".pdf"):

            path = os.path.join(DATA_FOLDER, filename)

            print(f"📄 Reading {filename}")

            reader = PdfReader(path)

            for page in reader.pages:

                text = page.extract_text()

                if text:

                    chunks = [
                        text[i:i+500]
                        for i in range(0, len(text), 500)
                    ]

                    for chunk in chunks:
                        documents.append(chunk)
                        ids.append(f"doc_{counter}")
                        counter += 1

    return ids, documents

ids, docs = extract_text_from_pdfs()

if docs:
    collection.add(
        ids=ids,
        documents=docs
    )

    print("✅ PDFs stored in ChromaDB")
else:
    print("⚠️ No text found")

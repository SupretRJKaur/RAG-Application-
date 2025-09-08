import os
import chromadb
from chromadb.utils import embedding_functions
from pypdf import PdfReader

# 1️⃣ Path to the data folder
DATA_FOLDER = "data"

# 2️⃣ Initialize ChromaDB (local database will be created)
client = chromadb.PersistentClient(path="./rag_db")

# 3️⃣ Create or get a collection (where embeddings are stored)
collection = client.get_or_create_collection(
    name="pdf_chunks",
    embedding_function=embedding_functions.DefaultEmbeddingFunction()
)

# 4️⃣ Read PDFs and chunk text
def extract_text_from_pdfs():
    documents = []
    ids = []
    i = 1

    for filename in os.listdir(DATA_FOLDER):
        if filename.endswith(".pdf"):
            file_path = os.path.join(DATA_FOLDER, filename)
            print(f"📄 Processing: {filename}")
            reader = PdfReader(file_path)
            
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    # Break into small chunks (500 characters)
                    chunks = [text[i:i+500] for i in range(0, len(text), 500)]
                    for chunk in chunks:
                        documents.append(chunk)
                        ids.append(f"doc_{i}")
                        i += 1
    return ids, documents

# 5️⃣ Extract and store embeddings
ids, documents = extract_text_from_pdfs()

if documents:
    print(f"✅ Storing {len(documents)} chunks in the database...")
    collection.add(ids=ids, documents=documents)
    print("🎉 Data added successfully!")
else:
    print("⚠️ No text found in PDFs.")

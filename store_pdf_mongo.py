import os
from dotenv import load_dotenv
import numpy as np
import json
import PyPDF2
from sentence_transformers import SentenceTransformer
from pymongo import MongoClient

load_dotenv()
# ─── MongoDB Atlas Setup ─────────────────────────────────────────────────────
# Expects your Atlas connection string in the MONGODB_URI environment variable:
#   export MONGODB_URI="mongodb+srv://<user>:<pass>@cluster0.xyz.mongodb.net/?retryWrites=true&w=majority"
MONGO_URI = os.getenv("MONGODB_URI") 
if not MONGO_URI:
    raise RuntimeError("Set the MONGODB_URI environment variable to your Atlas URI")

# Create a single, global client & collection reference
client = MongoClient(MONGO_URI, tls=True)
db = client["pdf_chunks_db"]
chunks_coll = db["chunks"]


def extract_text_from_pdf(pdf_path):
    """
    Extract all text from a PDF file.
    """
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
    return text


def chunk_text(text, max_length=2000, overlap=200):
    """
    Split text into chunks of approximately max_length characters with overlap.
    This approach preserves more context at chunk boundaries.
    """
    chunks = []
    if len(text) <= max_length:
        chunks.append(text)
    else:
        current_idx = 0
        while current_idx < len(text):
            chunk_end = min(current_idx + max_length, len(text))

            if chunk_end < len(text):
                # try to break on a paragraph
                paragraph_break = text.rfind('\n\n', current_idx, chunk_end)
                if paragraph_break != -1 and paragraph_break > current_idx + max_length//2:
                    chunk_end = paragraph_break + 2
                else:
                    # fallback: break on sentence end
                    sentence_break = max(
                        text.rfind('. ', current_idx, chunk_end),
                        text.rfind('! ', current_idx, chunk_end),
                        text.rfind('? ', current_idx, chunk_end)
                    )
                    if sentence_break != -1 and sentence_break > current_idx + max_length//2:
                        chunk_end = sentence_break + 2

            chunk = text[current_idx:chunk_end].strip()
            if chunk:
                chunks.append(chunk)

            current_idx = max(current_idx + max_length - overlap, chunk_end)
    return chunks


def index_pdfs(pdf_directory, model, chunk_size=500):
    """
    Process each PDF in the directory:
    1. Extract text.
    2. Chunk the text.
    3. Generate an embedding for each chunk.
    4. Collect embeddings and metadata.
    
    Returns:
        None, metadata_list
    """
    metadata = []

    for filename in os.listdir(pdf_directory):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(pdf_directory, filename)
            print(f"Processing {filename}...")
            text = extract_text_from_pdf(pdf_path)
            if not text.strip():
                continue

            chunks = chunk_text(text, max_length=chunk_size)
            for i, chunk in enumerate(chunks):
                embedding = model.encode(chunk)
                metadata.append({
                    'pdf_file': filename,
                    'chunk_index': i,
                    'chunk_text': chunk,
                    'embedding': embedding.tolist()
                })

    if metadata:
        print(f"Prepared {len(metadata)} chunks from PDFs.")
        return None, metadata
    else:
        print("No chunks to index.")
        return None, None


def save_index_and_metadata(faiss_index, metadata, index_file="faiss_index.index", metadata_file="metadata.json"):
    """
    Persist the chunk documents into MongoDB Atlas.
    """
    # clear out any old data
    chunks_coll.drop()
    # bulk-insert our new chunks
    chunks_coll.insert_many(metadata)
    print(f"Inserted {len(metadata)} chunks into MongoDB collection '{db.name}.{chunks_coll.name}'.")


def load_index_and_metadata(index_file="faiss_index.index", metadata_file="metadata.json"):
    """
    Load chunk documents back from MongoDB Atlas.
    """
    docs = list(chunks_coll.find({}, {'_id': False}))
    print(f"Loaded {len(docs)} chunks from MongoDB collection '{db.name}.{chunks_coll.name}'.")
    return None, docs


def retrieve_relevant_chunks(query, model, faiss_index, metadata, top_k=5):
    """
    Given a query, encode it, then do a brute-force L2 search
    over all embedded chunks to find the top_k closest.
    """
    query_emb = model.encode(query).astype(np.float32)
    distances = [
        np.linalg.norm(np.array(doc['embedding'], dtype=np.float32) - query_emb)
        for doc in metadata
    ]
    top_idxs = np.argsort(distances)[:top_k]
    return [metadata[i] for i in top_idxs]


def run_pdf_indexing(pdf_directory="downloaded_files", chunk_size=2000):
    """
    Build the chunk documents, store them in MongoDB Atlas, and
    allow a user to query them interactively.
    """
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # ensure the directory exists
    if not os.path.exists(pdf_directory):
        os.makedirs(pdf_directory)
        print(f"Created directory: {pdf_directory}")
        print("Please place your PDF files in this directory before continuing.")
        return

    # ensure there are PDFs to process
    if not any(fn.lower().endswith(".pdf") for fn in os.listdir(pdf_directory)):
        print(f"No PDF files found in {pdf_directory}. Please add some PDF files and run the script again.")
        return

    # extract, chunk, encode
    _, metadata = index_pdfs(pdf_directory, model, chunk_size=chunk_size)
    if not metadata:
        return

    # save into Atlas & reload
    save_index_and_metadata(None, metadata)
    _, metadata = load_index_and_metadata()

    # interactive query
    query = input("Enter your search query (e.g., 'create an APUSH study guide'): ")
    print(f"\nQuery: {query}")
    relevant_chunks = retrieve_relevant_chunks(query, model, None, metadata, top_k=5)

    print("\nRelevant chunks:")
    for chunk in relevant_chunks:
        print(f"File: {chunk['pdf_file']}, Chunk: {chunk['chunk_index']}")
        print(f"Snippet: {chunk['chunk_text'][:200]}...\n")


if __name__ == "__main__":
    run_pdf_indexing()

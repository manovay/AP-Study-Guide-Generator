# PDF Scraper and Vector Database Builder

This project automates the process of scraping PDFs from AP (Advanced Placement) websites, extracting their content, splitting the text into chunks, generating vector embeddings for each chunk, and storing these embeddings in a vector database (using FAISS). It uses **Poetry** for dependency management.

## How It Works

1. **Initial Setup**
   - The user provides a list of AP website URLs in `input_websites.csv`.
   - The project’s main script, `main.py`, orchestrates the entire workflow by calling two modules:
     - **Web Scraping Module:** Downloads PDFs from the provided AP websites.
     - **PDF Processing Module:** Extracts text from the downloaded PDFs, chunks the text, converts each chunk into a vector embedding using a SentenceTransformer model, and indexes these embeddings in a FAISS vector database.
   - Ensure that the required folder structure is in place (e.g., folders for downloaded PDFs, saved indexes, and metadata).

2. **Web Scraping**
   - The web scraping code loads each URL from `input_websites.csv`, navigates the site using Selenium, and downloads any PDF files found on those pages.
   - Downloaded PDFs are saved in the designated folder (e.g., `downloaded_files/`).

3. **PDF Processing and Vector Indexing**
   - The PDF processing module reads the downloaded PDFs and extracts text using PyPDF2.
   - The extracted text is split into manageable chunks to preserve context.
   - Each text chunk is converted into a vector embedding using a pre-trained model (e.g., `all-MiniLM-L6-v2` from SentenceTransformer).
   - All vector embeddings are then indexed using FAISS, and associated metadata is saved (e.g., PDF file name, chunk index, text snippet).

4. **Persistence**
   - The FAISS index and metadata are saved to disk for later retrieval, enabling quick and efficient similarity searches on the extracted content.

## Setup Instructions

1. **Install Dependencies**

   Ensure you have **Poetry** installed. In the project directory, run:

   ```bash
   poetry install
   ```

2. **Folder Structure**

   Ensure that the following folders exist (or are created automatically by the scripts):
   - `downloaded_files/` – for storing scraped PDF files.
   - (Optional) `faiss_index.index` and `metadata.json` – will be created after processing.

3. **Running the Project**

   To start the process—scraping the AP websites for PDFs, processing the PDFs, and building the vector database—run:

   ```bash
   poetry run python main.py
   ```

   This command will:
   - Scrape the URLs in `input_websites.csv` and download available PDFs.
   - Process the PDFs by extracting their content, chunking the text, generating vector embeddings, and storing the results in a FAISS vector index.

## Notes

- **PDF Warnings:**  
  You may see warnings such as `unknown widths` or `ignore '/Perms' verify failed` during PDF processing. These are common with PyPDF2 when encountering non-standard PDF structures or permission entries. They can typically be ignored unless they affect the text extraction quality.

- **Modularity:**  
  The project has been modularized so that web scraping and PDF processing are contained in separate modules. This makes it easier to test, maintain, and extend the functionality.

- **Customization:**  
  You can customize parameters such as the maximum chunk size or the model used for vector embeddings by modifying the respective modules.

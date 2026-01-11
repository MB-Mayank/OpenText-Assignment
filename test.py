"""
COMPLETE RAG PIPELINE - SIMPLIFIED & CLEAN
Crawl → Extract → Chunk → Embed → Store in ChromaDB
Each chunk has proper metadata mapping
"""

import requests
from bs4 import BeautifulSoup
import PyPDF2
from typing import List, Dict
from datetime import datetime
import hashlib
import time
import os
import numpy as np

# ============================================
# COMPLETE RAG SYSTEM - SIMPLIFIED
# ============================================

class CompleteRAGSystem:
    """
    Simplified RAG system with only multiple-document functions
    """
    
    def __init__(self, 
                 chunk_size: int = 500,
                 chunk_overlap: int = 50,
                 hf_token: str = None,
                 embedding_model: str = 'sentence-transformers/all-MiniLM-L6-v2'):
        """
        Initialize the complete RAG system with HuggingFace
        
        Args:
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            hf_token: HuggingFace API token (get from huggingface.co/settings/tokens)
            embedding_model: HuggingFace model for embeddings
        """
        print("="*80)
        print("INITIALIZING COMPLETE RAG SYSTEM WITH HUGGINGFACE")
        print("="*80)
        
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.hf_token = hf_token
        self.embedding_model_name = embedding_model
        
        # HuggingFace API endpoint
        self.hf_api_url = f"https://api-inference.huggingface.co/models/{embedding_model}"
        
        # Initialize headers for HuggingFace API
        self.hf_headers = {}
        if hf_token:
            self.hf_headers["Authorization"] = f"Bearer {hf_token}"
        
        print(f"\n[1/2] Using HuggingFace embedding model: {embedding_model}")
        if hf_token:
            print("✓ HuggingFace API token provided")
        else:
            print("⚠️  No HuggingFace token - using public inference (may have rate limits)")
        
        # Initialize in-memory vector store (replacing ChromaDB)
        self.vector_store = {
            'ids': [],
            'embeddings': [],
            'documents': [],
            'metadatas': []
        }
        
        print(f"\n[2/2] Initialized in-memory vector store")
        
        # Request headers for web crawling
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        print(f"\n✓ System ready!")
        print("="*80 + "\n")
    
    # ========================================
    # WEB CRAWLING - MULTIPLE WEBSITES
    # ========================================
    
    def crawl_websites(self, urls: List[str]) -> List[Dict]:
        """
        Crawl multiple websites - each with its own metadata
        
        Args:
            urls: List of URLs to crawl
            
        Returns:
            List of results, each containing content and metadata
        """
        print("\n" + "="*80)
        print("CRAWLING WEBSITES")
        print("="*80 + "\n")
        
        results = []
        
        for i, url in enumerate(urls, 1):
            print(f"[{i}/{len(urls)}] 🌐 Crawling: {url}")
            
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract metadata for THIS website
                metadata = {
                    'source_type': 'web',
                    'url': url,
                    'title': '',
                    'site_name': '',
                    'access_date': datetime.now().strftime('%Y-%m-%d'),
                    'author': '',
                    'description': ''
                }
                
                # Extract title
                title_tag = soup.find('title')
                metadata['title'] = title_tag.get_text().strip() if title_tag else "No Title"
                
                # Extract site name
                from urllib.parse import urlparse
                domain = urlparse(url).netloc
                metadata['site_name'] = domain.replace('www.', '')
                
                # Extract author
                author_meta = soup.find('meta', attrs={'name': 'author'})
                if author_meta and author_meta.get('content'):
                    metadata['author'] = author_meta.get('content')
                
                # Extract description
                desc_meta = soup.find('meta', attrs={'name': 'description'})
                if desc_meta and desc_meta.get('content'):
                    metadata['description'] = desc_meta.get('content')
                
                # Remove unwanted elements
                for element in soup(["script", "style", "nav", "footer", "header"]):
                    element.decompose()
                
                # Extract content
                main_content = soup.find('main') or soup.find('article') or soup.find('body')
                if main_content:
                    text = main_content.get_text(separator='\n', strip=True)
                else:
                    text = soup.get_text(separator='\n', strip=True)
                
                # Clean text
                lines = [line.strip() for line in text.splitlines() if line.strip()]
                content = '\n'.join(lines)
                
                print(f"   ✓ Extracted {len(content)} characters from '{metadata['title']}'")
                
                results.append({
                    'content': content,
                    'metadata': metadata,  # Each website has its own metadata
                    'status': 'success'
                })
                
            except Exception as e:
                print(f"   ✗ Error: {str(e)}")
                results.append({
                    'content': '',
                    'metadata': {'url': url, 'title': 'Error', 'source_type': 'web'},
                    'status': f'failed: {str(e)}'
                })
            
            time.sleep(1)  # Be polite between requests
        
        successful = sum(1 for r in results if r['status'] == 'success')
        print(f"\n✓ Crawled {successful}/{len(urls)} websites successfully\n")
        
        return results
    
    # ========================================
    # PDF EXTRACTION - MULTIPLE PDFs
    # ========================================
    
    def extract_pdfs(self, pdf_paths: List[str]) -> List[Dict]:
        """
        Extract from multiple PDFs - each with its own metadata
        
        Args:
            pdf_paths: List of PDF file paths
            
        Returns:
            List of results, each containing content and metadata
        """
        print("\n" + "="*80)
        print("EXTRACTING PDFs")
        print("="*80 + "\n")
        
        results = []
        
        for i, pdf_path in enumerate(pdf_paths, 1):
            print(f"[{i}/{len(pdf_paths)}] 📄 Extracting: {pdf_path}")
            
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    
                    # Extract metadata for THIS PDF
                    metadata = {
                        'source_type': 'pdf',
                        'filename': os.path.basename(pdf_path),
                        'file_path': pdf_path,
                        'num_pages': len(pdf_reader.pages),
                        'extraction_date': datetime.now().strftime('%Y-%m-%d'),
                        'title': '',
                        'author': '',
                        'subject': ''
                    }
                    
                    # Get PDF metadata
                    if pdf_reader.metadata:
                        metadata['title'] = pdf_reader.metadata.get('/Title', '')
                        metadata['author'] = pdf_reader.metadata.get('/Author', '')
                        metadata['subject'] = pdf_reader.metadata.get('/Subject', '')
                    
                    # Extract text
                    full_text = ""
                    for page_num in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_num]
                        full_text += page.extract_text() + "\n"
                    
                    # If no title, use first line or filename
                    if not metadata['title']:
                        first_line = full_text.split('\n')[0].strip()
                        metadata['title'] = first_line[:100] if first_line else metadata['filename']
                    
                    print(f"   ✓ Extracted {len(full_text)} characters from {len(pdf_reader.pages)} pages")
                    
                    results.append({
                        'content': full_text.strip(),
                        'metadata': metadata,  # Each PDF has its own metadata
                        'status': 'success'
                    })
                    
            except Exception as e:
                print(f"   ✗ Error: {str(e)}")
                results.append({
                    'content': '',
                    'metadata': {
                        'filename': os.path.basename(pdf_path) if pdf_path else 'Unknown',
                        'source_type': 'pdf',
                        'error': str(e)
                    },
                    'status': f'failed: {str(e)}'
                })
        
        successful = sum(1 for r in results if r['status'] == 'success')
        print(f"\n✓ Extracted {successful}/{len(pdf_paths)} PDFs successfully\n")
        
        return results
    
    # ========================================
    # CHUNKING - PRESERVES METADATA
    # ========================================
    
    def chunk_documents(self, documents: List[Dict]) -> List[Dict]:
        """
        Chunk all documents - each chunk inherits parent metadata
        
        Args:
            documents: List of documents with content and metadata
            
        Returns:
            List of chunks, each with text and full metadata
        """
        print("\n" + "="*80)
        print("CHUNKING DOCUMENTS")
        print("="*80 + "\n")
        
        all_chunks = []
        
        for doc in documents:
            if doc['status'] == 'success' and doc['content']:
                
                # Chunk this document
                content = doc['content']
                parent_metadata = doc['metadata']
                
                sentences = content.replace('\n', ' ').split('. ')
                current_chunk = ""
                chunk_index = 0
                
                for sentence in sentences:
                    sentence = sentence.strip() + ". "
                    
                    if len(current_chunk) + len(sentence) > self.chunk_size and current_chunk:
                        # Save chunk with parent metadata + chunk metadata
                        chunk_id = self._generate_chunk_id(parent_metadata, chunk_index)
                        
                        all_chunks.append({
                            'text': current_chunk.strip(),
                            'metadata': {
                                **parent_metadata,  # All parent metadata (website or PDF)
                                'chunk_index': chunk_index,
                                'chunk_id': chunk_id,
                                'chunk_length': len(current_chunk)
                            }
                        })
                        
                        # Start new chunk with overlap
                        overlap = current_chunk[-self.chunk_overlap:] if len(current_chunk) > self.chunk_overlap else current_chunk
                        current_chunk = overlap + sentence
                        chunk_index += 1
                    else:
                        current_chunk += sentence
                
                # Add last chunk
                if current_chunk.strip():
                    chunk_id = self._generate_chunk_id(parent_metadata, chunk_index)
                    all_chunks.append({
                        'text': current_chunk.strip(),
                        'metadata': {
                            **parent_metadata,
                            'chunk_index': chunk_index,
                            'chunk_id': chunk_id,
                            'chunk_length': len(current_chunk)
                        }
                    })
                
                source_name = parent_metadata.get('title') or parent_metadata.get('filename', 'Unknown')
                num_chunks = chunk_index + 1
                print(f"✓ Chunked '{source_name}': {num_chunks} chunks")
        
        print(f"\n✓ Total chunks created: {len(all_chunks)}\n")
        return all_chunks
    
    def _generate_chunk_id(self, metadata: Dict, chunk_index: int) -> str:
        """Generate unique chunk ID"""
        source_id = metadata.get('url') or metadata.get('filename', 'unknown')
        chunk_str = f"{source_id}_{chunk_index}"
        return hashlib.md5(chunk_str.encode()).hexdigest()[:16]
    
    # ========================================
    # HUGGINGFACE EMBEDDINGS
    # ========================================
    
    def _generate_embeddings_hf(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using HuggingFace API
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        
        print(f"🧠 Generating embeddings using HuggingFace API...")
        
        # Process in batches to avoid API limits
        batch_size = 10
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            
            try:
                response = requests.post(
                    self.hf_api_url,
                    headers=self.hf_headers,
                    json={"inputs": batch_texts, "options": {"wait_for_model": True}}
                )
                
                if response.status_code == 200:
                    batch_embeddings = response.json()
                    embeddings.extend(batch_embeddings)
                    print(f"   ✓ Generated embeddings for batch {i//batch_size + 1} ({i+1}-{min(i+batch_size, len(texts))})")
                else:
                    print(f"   ✗ Error in batch {i//batch_size + 1}: {response.status_code}")
                    # Use zero vectors as fallback
                    embeddings.extend([[0.0] * 384] * len(batch_texts))
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"   ✗ Exception in batch {i//batch_size + 1}: {str(e)}")
                embeddings.extend([[0.0] * 384] * len(batch_texts))
        
        return embeddings
    
    # ========================================
    # VECTOR STORAGE - WITH METADATA
    # ========================================
    
    def store_in_vector_db(self, chunks: List[Dict], collection_name: str = "rag_collection"):
        """
        Store chunks in vector store with HuggingFace embeddings
        
        Args:
            chunks: List of chunks with text and metadata
            collection_name: Collection name (for compatibility)
        """
        print("="*80)
        print("GENERATING EMBEDDINGS & STORING IN VECTOR DATABASE")
        print("="*80 + "\n")
        
        # Clear existing store
        self.vector_store = {
            'ids': [],
            'embeddings': [],
            'documents': [],
            'metadatas': []
        }
        print(f"✓ Initialized vector store: {collection_name}\n")
        
        # Extract texts
        texts = [chunk['text'] for chunk in chunks]
        
        # Generate embeddings using HuggingFace
        embeddings = self._generate_embeddings_hf(texts)
        print("✓ Embeddings generated\n")
        
        # Prepare data - each chunk has its metadata
        ids = [chunk['metadata']['chunk_id'] for chunk in chunks]
        metadatas = [self._clean_metadata(chunk['metadata']) for chunk in chunks]
        
        # Store in vector database
        print("💾 Storing in vector database...")
        self.vector_store['ids'] = ids
        self.vector_store['embeddings'] = embeddings
        self.vector_store['documents'] = texts
        self.vector_store['metadatas'] = metadatas
        
        print(f"\n✓ Successfully stored {len(chunks)} chunks with metadata")
        print(f"✓ Collection: {collection_name}")
        print(f"✓ Total documents: {len(self.vector_store['ids'])}\n")
        
        return self.vector_store
    
    def _clean_metadata(self, metadata: Dict) -> Dict:
        """Clean metadata for storage"""
        clean = {}
        for key, value in metadata.items():
            if value is None:
                clean[key] = "N/A"
            elif isinstance(value, (str, int, float, bool)):
                clean[key] = value
            else:
                clean[key] = str(value)
        return clean
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    # ========================================
    # QUERY - RETRIEVES WITH METADATA
    # ========================================
    
    def query(self, query_text: str, collection_name: str = "rag_collection", n_results: int = 3):
        """
        Query the RAG system using HuggingFace embeddings
        
        Args:
            query_text: Query string
            collection_name: Collection name (for compatibility)
            n_results: Number of results
            
        Returns:
            Results with text and metadata
        """
        print("\n" + "="*80)
        print(f"QUERYING: '{query_text}'")
        print("="*80 + "\n")
        
        # Generate query embedding using HuggingFace
        query_embedding = self._generate_embeddings_hf([query_text])[0]
        
        # Calculate similarities
        similarities = []
        for i, doc_embedding in enumerate(self.vector_store['embeddings']):
            similarity = self._cosine_similarity(query_embedding, doc_embedding)
            similarities.append((i, similarity))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Get top n results
        top_results = similarities[:n_results]
        
        # Prepare results
        results = {
            'documents': [[]],
            'metadatas': [[]],
            'distances': [[]]
        }
        
        for idx, similarity in top_results:
            results['documents'][0].append(self.vector_store['documents'][idx])
            results['metadatas'][0].append(self.vector_store['metadatas'][idx])
            results['distances'][0].append(1 - similarity)  # Convert similarity to distance
        
        # Display results with metadata
        for i, (doc, metadata, distance) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        ), 1):
            print(f"[RESULT {i}] Similarity: {1-distance:.3f}")
            print(f"─" * 80)
            print(f"Source Type: {metadata.get('source_type', 'N/A')}")
            print(f"Title: {metadata.get('title', 'N/A')}")
            
            if metadata.get('source_type') == 'web':
                print(f"URL: {metadata.get('url', 'N/A')}")
                print(f"Site: {metadata.get('site_name', 'N/A')}")
                print(f"Author: {metadata.get('author', 'N/A')}")
                print(f"Access Date: {metadata.get('access_date', 'N/A')}")
            else:
                print(f"Filename: {metadata.get('filename', 'N/A')}")
                print(f"Author: {metadata.get('author', 'N/A')}")
                print(f"Pages: {metadata.get('num_pages', 'N/A')}")
            
            print(f"Chunk Index: {metadata.get('chunk_index', 'N/A')}")
            print(f"\nText: {doc[:300]}...")
            print("=" * 80 + "\n")
        
        return results


# ============================================
# MAIN USAGE
# ============================================

if __name__ == "__main__":
    
    # Initialize system with HuggingFace
    # Get your HuggingFace token from: https://huggingface.co/settings/tokens
    HF_TOKEN = "your_huggingface_token_here"  # Replace with your token or set to None for public API
    
    rag = CompleteRAGSystem(
        chunk_size=500,
        chunk_overlap=50,
        hf_token=HF_TOKEN,  # Optional: add your HuggingFace token for better rate limits
        embedding_model='sentence-transformers/all-MiniLM-L6-v2'
    )
    
    # ========================================
    # STEP 1: CRAWL WEBSITES
    # Each website gets its own metadata
    # ========================================
    
    websites = [
        "https://en.wikipedia.org/wiki/Natural_language_processing",
        "https://en.wikipedia.org/wiki/Transformer_(machine_learning_model)",
        "https://en.wikipedia.org/wiki/Large_language_model",
        "https://en.wikipedia.org/wiki/Retrieval-augmented_generation"
    ]
    
    web_results = rag.crawl_websites(websites)
    
    # ========================================
    # STEP 2: EXTRACT PDFs
    # Each PDF gets its own metadata
    # ========================================
    
    pdf_files = [
        "paper1.pdf",
        "paper2.pdf",
        "paper3.pdf"
    ]
    
    # Only process existing PDFs
    existing_pdfs = [pdf for pdf in pdf_files if os.path.exists(pdf)]
    
    if existing_pdfs:
        pdf_results = rag.extract_pdfs(existing_pdfs)
    else:
        print("\n⚠️  No PDF files found. Skipping PDF extraction.")
        print("   Place your PDFs in the same directory and update pdf_files list.\n")
        pdf_results = []
    
    # ========================================
    # STEP 3: COMBINE ALL DOCUMENTS
    # ========================================
    
    all_documents = web_results + pdf_results
    
    # ========================================
    # STEP 4: CHUNK DOCUMENTS
    # Each chunk inherits parent metadata
    # ========================================
    
    all_chunks = rag.chunk_documents(all_documents)
    
    # Show example chunk with full metadata
    if all_chunks:
        print("="*80)
        print("EXAMPLE CHUNK WITH FULL METADATA")
        print("="*80)
        example = all_chunks[0]
        print(f"\nChunk Text: {example['text'][:200]}...")
        print(f"\nFull Metadata (inherited from parent + chunk info):")
        for key, value in example['metadata'].items():
            print(f"  {key}: {value}")
        print("\n")
    
    # ========================================
    # STEP 5: STORE IN VECTOR DATABASE
    # Each chunk stored with its metadata using HuggingFace embeddings
    # ========================================
    
    vector_store = rag.store_in_vector_db(all_chunks, collection_name="rag_collection")
    
    # ========================================
    # STEP 6: TEST QUERIES
    # Retrieved chunks include full metadata
    # ========================================
    
    rag.query("What is natural language processing?", n_results=3)
    rag.query("Explain transformer models", n_results=3)
    rag.query("What is RAG?", n_results=3)
    
    print("="*80)
    print("✅ COMPLETE RAG SYSTEM WITH HUGGINGFACE")
    print("="*80)
    print("\n✓ Each website has its own metadata")
    print("✓ Each PDF has its own metadata")
    print("✓ Each chunk inherits parent metadata + adds chunk info")
    print("✓ Embeddings generated using HuggingFace API")
    print("✓ All metadata stored in vector database")
    print("✓ Queries return chunks with full citation data")
    print("\nNext: Integrate with Groq LLM for intelligent responses!")
    print("="*80)

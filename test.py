"""
RAG System with Groq LLM, LangChain, ChromaDB, and HuggingFace Embeddings
Features: Web crawling, PDF scraping, proper chunking, metadata, and citations
"""

import os
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document
import requests
from bs4 import BeautifulSoup
import PyPDF2
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ===========================================
# CONFIGURATION
# ===========================================

GROQ_API_KEY = "your_groq_api_key_here"  # Replace with your actual key
os.environ["GROQ_API_KEY"] = GROQ_API_KEY

# 4 Websites to crawl
WEBSITES = [
    "https://en.wikipedia.org/wiki/Artificial_intelligence",
    "https://en.wikipedia.org/wiki/Machine_learning",
    "https://en.wikipedia.org/wiki/Natural_language_processing",
    "https://en.wikipedia.org/wiki/Transformer_(machine_learning_model)"
]

# 4 PDF files (place your research papers in the same directory)
PDF_FILES = [
    "paper1.pdf",
    "paper2.pdf",
    "paper3.pdf",
    "paper4.pdf"
]

# ChromaDB settings
CHROMA_PERSIST_DIR = "./chroma_db"
COLLECTION_NAME = "rag_collection"

# ===========================================
# TOOL 1: WEB CRAWLER
# ===========================================

class WebCrawler:
    """Tool to crawl web pages and extract content with metadata"""
    
    @staticmethod
    def crawl(url):
        """
        Crawl a webpage and extract text content
        
        Args:
            url (str): URL to crawl
        
        Returns:
            Document: LangChain Document with content and metadata
        """
        try:
            print(f"🌐 Crawling: {url}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.title.string if soup.title else url.split('/')[-1]
            
            # Remove unwanted elements
            for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
                element.decompose()
            
            # Get text content
            text = soup.get_text(separator=' ', strip=True)
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Create metadata
            metadata = {
                'source': url,
                'source_type': 'web',
                'title': title,
                'crawled_date': datetime.now().isoformat(),
                'length': len(text)
            }
            
            print(f"  ✓ Successfully crawled ({len(text):,} chars)")
            
            return Document(page_content=text, metadata=metadata)
        
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            return None

# ===========================================
# TOOL 2: RESEARCH PAPER SCRAPER
# ===========================================

class PDFScraper:
    """Tool to scrape PDF research papers with metadata"""
    
    @staticmethod
    def scrape(pdf_path):
        """
        Extract text from a PDF file
        
        Args:
            pdf_path (str): Path to PDF file
        
        Returns:
            Document: LangChain Document with content and metadata
        """
        try:
            print(f"📄 Scraping PDF: {pdf_path}")
            text = ""
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                # Extract text from all pages
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
                
                # Get PDF metadata
                pdf_metadata = pdf_reader.metadata if pdf_reader.metadata else {}
            
            # Create comprehensive metadata
            metadata = {
                'source': pdf_path,
                'source_type': 'pdf',
                'title': pdf_metadata.get('/Title', pdf_path.split('/')[-1]),
                'author': pdf_metadata.get('/Author', 'Unknown'),
                'num_pages': num_pages,
                'scraped_date': datetime.now().isoformat(),
                'length': len(text)
            }
            
            print(f"  ✓ Successfully scraped ({num_pages} pages, {len(text):,} chars)")
            
            return Document(page_content=text, metadata=metadata)
        
        except FileNotFoundError:
            print(f"  ✗ File not found: {pdf_path}")
            return None
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            return None

# ===========================================
# DATA COLLECTION
# ===========================================

def collect_all_documents():
    """
    Collect documents from all sources (web + PDF)
    
    Returns:
        list: List of LangChain Documents with metadata
    """
    documents = []
    
    print("\n" + "="*60)
    print("📚 COLLECTING DATA FROM ALL SOURCES")
    print("="*60)
    
    # Crawl websites
    print("\n🌐 WEB CRAWLING")
    print("-"*60)
    for url in WEBSITES:
        doc = WebCrawler.crawl(url)
        if doc:
            documents.append(doc)
    
    # Scrape PDFs
    print("\n📄 PDF SCRAPING")
    print("-"*60)
    for pdf_file in PDF_FILES:
        doc = PDFScraper.scrape(pdf_file)
        if doc:
            documents.append(doc)
    
    print("\n" + "="*60)
    print(f"✅ Total documents collected: {len(documents)}")
    print("="*60)
    
    return documents

# ===========================================
# CHUNKING WITH METADATA
# ===========================================

def chunk_documents(documents):
    """
    Split documents into chunks while preserving metadata
    
    Args:
        documents (list): List of LangChain Documents
    
    Returns:
        list: List of chunked Documents with metadata
    """
    print("\n" + "="*60)
    print("✂️  CHUNKING DOCUMENTS")
    print("="*60)
    
    # Initialize text splitter with overlap for context preservation
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    all_chunks = []
    
    for doc in documents:
        # Split the document
        chunks = text_splitter.split_documents([doc])
        
        # Add chunk-specific metadata
        for i, chunk in enumerate(chunks):
            chunk.metadata['chunk_id'] = i
            chunk.metadata['total_chunks'] = len(chunks)
            chunk.metadata['chunk_size'] = len(chunk.page_content)
        
        all_chunks.extend(chunks)
        
        print(f"  {doc.metadata['source_type'].upper()}: {doc.metadata.get('title', 'Unknown')[:50]}")
        print(f"    → Split into {len(chunks)} chunks")
    
    print(f"\n✅ Total chunks created: {len(all_chunks)}")
    print("="*60)
    
    return all_chunks

# ===========================================
# VECTOR DATABASE SETUP
# ===========================================

def setup_vectordb(chunks):
    """
    Create ChromaDB vector database with HuggingFace embeddings
    
    Args:
        chunks (list): List of document chunks
    
    Returns:
        Chroma: Vector database instance
    """
    print("\n" + "="*60)
    print("🗄️  SETTING UP VECTOR DATABASE (ChromaDB)")
    print("="*60)
    
    # Initialize HuggingFace embeddings
    print("\n📊 Loading HuggingFace embedding model...")
    print("   Model: sentence-transformers/all-MiniLM-L6-v2")
    
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    print("   ✓ Embedding model loaded successfully")
    
    # Create ChromaDB vector store
    print(f"\n💾 Creating ChromaDB collection: '{COLLECTION_NAME}'")
    print(f"   Persist directory: {CHROMA_PERSIST_DIR}")
    print(f"   Storing {len(chunks)} chunks with embeddings...")
    
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_PERSIST_DIR
    )
    
    print("   ✓ Vector database created successfully")
    print("="*60)
    
    return vectordb

# ===========================================
# LLM SETUP
# ===========================================

def setup_llm():
    """
    Initialize Groq LLM with LangChain
    
    Returns:
        ChatGroq: LLM instance
    """
    print("\n" + "="*60)
    print("🤖 SETTING UP GROQ LLM")
    print("="*60)
    
    llm = ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name="mixtral-8x7b-32768",  # You can also use "llama2-70b-4096"
        temperature=0.3,
        max_tokens=1024
    )
    
    # Test the LLM
    print("\n🧪 Testing LLM connection...")
    test_response = llm.invoke("Say 'Hello! I am ready to assist with RAG queries.'")
    print(f"   Response: {test_response.content}")
    print("   ✓ LLM is working correctly")
    print("="*60)
    
    return llm

# ===========================================
# RAG SYSTEM
# ===========================================

def create_rag_chain(vectordb, llm):
    """
    Create RAG chain with custom prompt template including citations
    
    Args:
        vectordb (Chroma): Vector database
        llm: Language model
    
    Returns:
        RetrievalQA: RAG chain
    """
    print("\n" + "="*60)
    print("🔗 CREATING RAG CHAIN")
    print("="*60)
    
    # Custom prompt template with citation instructions
    prompt_template = """You are a helpful AI assistant that answers questions based on the provided context. 
Always cite your sources by mentioning the source type (web/pdf) and title.

Context from knowledge base:
{context}

Question: {question}

Instructions:
1. Answer the question based on the context provided
2. Cite your sources (mention if from web or PDF and the title)
3. If the context doesn't contain relevant information, say so
4. Be concise and accurate

Answer:"""

    PROMPT = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )
    
    # Create retriever with metadata
    retriever = vectordb.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}  # Retrieve top 4 most relevant chunks
    )
    
    # Create RAG chain
    rag_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT}
    )
    
    print("   ✓ RAG chain created successfully")
    print("   Retrieval strategy: Similarity search (top 4 chunks)")
    print("="*60)
    
    return rag_chain

# ===========================================
# QUERY FUNCTION WITH CITATIONS
# ===========================================

def query_rag_system(rag_chain, question):
    """
    Query the RAG system and display results with citations
    
    Args:
        rag_chain: RAG chain instance
        question (str): User question
    """
    print("\n" + "="*60)
    print(f"❓ QUERY: {question}")
    print("="*60)
    
    # Get response
    result = rag_chain.invoke({"query": question})
    
    # Display answer
    print("\n💡 ANSWER:")
    print("-"*60)
    print(result['result'])
    
    # Display source citations
    print("\n📚 SOURCES & CITATIONS:")
    print("-"*60)
    
    for i, doc in enumerate(result['source_documents'], 1):
        print(f"\n{i}. Source Type: {doc.metadata.get('source_type', 'Unknown').upper()}")
        print(f"   Title: {doc.metadata.get('title', 'Unknown')}")
        print(f"   Source: {doc.metadata.get('source', 'Unknown')}")
        print(f"   Chunk: {doc.metadata.get('chunk_id', '?')} / {doc.metadata.get('total_chunks', '?')}")
        print(f"   Preview: {doc.page_content[:200]}...")
    
    print("\n" + "="*60)

# ===========================================
# MAIN EXECUTION
# ===========================================

def main():
    """Main execution function"""
    
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█" + "  RAG SYSTEM - Groq + LangChain + ChromaDB + HF".center(58) + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    
    # Step 1: Collect documents
    documents = collect_all_documents()
    
    if not documents:
        print("\n❌ No documents collected. Please check your sources.")
        return
    
    # Step 2: Chunk documents with metadata
    chunks = chunk_documents(documents)
    
    # Step 3: Setup vector database
    vectordb = setup_vectordb(chunks)
    
    # Step 4: Setup LLM
    llm = setup_llm()
    
    # Step 5: Create RAG chain
    rag_chain = create_rag_chain(vectordb, llm)
    
    # Step 6: Example queries
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█" + "  RUNNING EXAMPLE QUERIES".center(58) + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    
    example_queries = [
        "What is artificial intelligence?",
        "Explain machine learning and its applications",
        "What are transformer models in NLP?",
        "What are the latest methods for improving transformer architectures?"
    ]
    
    for query in example_queries:
        query_rag_system(rag_chain, query)
        print("\n")
    
    # Interactive mode
    print("\n" + "="*60)
    print("🎯 INTERACTIVE MODE")
    print("="*60)
    print("You can now ask questions. Type 'quit' to exit.\n")
    
    while True:
        user_query = input("Your question: ").strip()
        
        if user_query.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Goodbye!")
            break
        
        if user_query:
            query_rag_system(rag_chain, user_query)

if __name__ == "__main__":
    main()

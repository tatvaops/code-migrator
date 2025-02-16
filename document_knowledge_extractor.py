import os
from typing import List, Dict
from docx import Document
import markdown
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

class DocumentExtractor:
    def __init__(self, persist_directory: str = "./vector_db"):
        self.persist_directory = persist_directory
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_store = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
    
    def extract_from_docx(self, file_path: str) -> str:
        """Extract text content from Word document"""
        doc = Document(file_path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    
    def extract_from_markdown(self, file_path: str) -> str:
        """Extract text content from Markdown file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
            html = markdown.markdown(md_content)
            soup = BeautifulSoup(html, 'html.parser')
            return soup.get_text()
    
    def process_documents(self, source_dir: str) -> Dict[str, str]:
        """Process all documents in the source directory"""
        document_contents = {}
        
        for root, _, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if file.endswith('.docx'):
                    content = self.extract_from_docx(file_path)
                    document_contents[file_path] = content
                elif file.endswith('.md'):
                    content = self.extract_from_markdown(file_path)
                    document_contents[file_path] = content
        
        return document_contents
    
    def create_vector_store(self, document_contents: Dict[str, str]):
        """Create vector store from document contents"""
        texts = []
        metadatas = []
        
        for file_path, content in document_contents.items():
            chunks = self.text_splitter.split_text(content)
            texts.extend(chunks)
            metadatas.extend([{"source": file_path} for _ in chunks])
        
        self.vector_store = Chroma.from_texts(
            texts=texts,
            embedding=self.embeddings,
            metadatas=metadatas,
            persist_directory=self.persist_directory
        )
    
    def query_similar_content(self, query: str, num_results: int = 5) -> List[Dict]:
        """Query the vector store for similar content"""
        if not self.vector_store:
            raise ValueError("Vector store not initialized. Process documents first.")
        
        results = self.vector_store.similarity_search_with_score(query, k=num_results)
        return [{"content": doc.page_content, 
                "source": doc.metadata["source"],
                "similarity": score} 
                for doc, score in results]
    
    def close(self):
        """Cleanup resources"""
        if self.vector_store:
            self.vector_store.persist() 
"""
Módulo para cargar y procesar documentos TXT y PDF
"""

import os
from typing import List
from pypdf import PdfReader


class DocumentLoader:

    """Clase para cargar documentos desde archivos locales"""
    
    def __init__(self, documents_path: str):
        self.documents_path = documents_path
        
    def load_txt(self, filepath: str) -> str:

        """Cargar archivo TXT"""

        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    
    def load_pdf(self, filepath: str) -> str:
        
        """Cargar archivo PDF"""

        reader = PdfReader(filepath)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    
    def load_all_documents(self) -> List[dict]:

        """
        Cargar todos los documentos TXT y PDF del directorio
        Retorna lista de diccionarios con 'content' y 'metadata'
        """

        if not os.path.exists(self.documents_path):
            raise FileNotFoundError(
                f"No existe el directorio: {self.documents_path}"
            )
        
        documents = []
        
        for filename in os.listdir(self.documents_path):
            filepath = os.path.join(self.documents_path, filename)
            
            if not os.path.isfile(filepath):
                continue
            
            try:
                if filename.endswith('.txt'):
                    content = self.load_txt(filepath)
                elif filename.endswith('.pdf'):
                    content = self.load_pdf(filepath)
                else:
                    continue
                
                documents.append({
                    'content': content,
                    'metadata': {
                        'source': filename,
                        'type': filename.split('.')[-1]
                    }
                })
                print(f"Cargado: {filename}")
                
            except Exception as e:
                print(f"Error cargando {filename}: {e}")
        
        return documents
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:

        """
        Dividir texto en chunks con overlap
        """
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
        
        return chunks
"""
Módulo para cargar y procesar documentos TXT y PDF
"""

import os
from typing import List
from pypdf import PdfReader
import re
import logging
import config

logger = logging.getLogger(__name__)


class DocumentLoader:

    """Clase para cargar documentos desde archivos locales"""
    
    ALLOWED_EXTENSIONS = {'.txt', '.pdf'}

    def __init__(self, documents_path: str):
        self.documents_path = documents_path
        self.max_file_bytes = config.MAX_DOCUMENT_FILE_MB * 1024 * 1024

    def _sanitize_text(self, text: str) -> str:
        return re.sub(
            r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]',
            '',
            text
        ).strip()

    def _validate_size(self, filepath: str):

        file_size = os.path.getsize(filepath)

        if file_size > self.max_file_bytes:
            raise ValueError(
                f"Archivo demasiado grande: {file_size} bytes"
            )

    def _validate_extension(self, filename: str):

        ext = os.path.splitext(filename)[1].lower()

        if ext not in self.ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Extensión no permitida: {ext}"
            )
        
    def load_txt(self, filepath: str) -> str:

        """Cargar archivo TXT"""

        self._validate_size(filepath)

        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()

        return self._sanitize_text(text)

    def load_pdf(self, filepath: str) -> str:
        
        """Cargar archivo PDF"""

        self._validate_size(filepath)

        reader = PdfReader(filepath)
        text = ""

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        return self._sanitize_text(text)

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
                # Validar extensión permitida
                self._validate_extension(filename)

                if filename.endswith('.txt'):
                    content = self.load_txt(filepath)

                elif filename.endswith('.pdf'):
                    content = self.load_pdf(filepath)
                
                documents.append({
                    'content': content,
                    'metadata': {
                        'source': filename,
                        'type': filename.split('.')[-1]
                    }
                })

                logger.info(f" Documento cargado: {filename}")
                
            except Exception as e:
                logger.warning(f"Archivo rechazado ({filename}): {e}")
        
        return documents
    
    def chunk_text(self, text: str, chunk_size: int = config.CHUNK_SIZE, overlap: int = config.CHUNK_OVERLAP) -> List[str]:

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
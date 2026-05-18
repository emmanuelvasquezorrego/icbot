"""
Módulo para gestión de Qdrant y embeddings
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import uuid
import config
import shutil
import os
import time
import logging

logger = logging.getLogger(__name__)

logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
logging.getLogger("transformers").setLevel(logging.WARNING)


class VectorStore:

    """Clase para gestionar Qdrant con sentence-transformers"""
    
    def __init__(self):
        # Inicializar cliente Qdrant
        if config.QDRANT_HOST and config.QDRANT_PORT:
            # Modo cliente-servidor (Docker/Cloud)
            logger.info(f"Conectando a Qdrant en {config.QDRANT_HOST}:{config.QDRANT_PORT}")
            self.client = QdrantClient(
                host=config.QDRANT_HOST,
                port=config.QDRANT_PORT
            )
            self.embedded_mode = False
        else:
            # Modo embebido (sin Docker)
            logger.info(f"Iniciando Qdrant en modo local: {config.QDRANT_PATH}")
            self.client = QdrantClient(path=config.QDRANT_PATH)
            self.embedded_mode = True
        
        # Cargar modelo de embeddings
        logger.info(f"Cargando modelo de embeddings: {config.EMBEDDING_MODEL}")
        self.embedding_model = SentenceTransformer(config.EMBEDDING_MODEL)
        
        # Crear colección si no existe
        self._create_collection_if_not_exists()
    
    def _create_collection_if_not_exists(self):

        """Crear colección en Qdrant si no existe"""

        collections = self.client.get_collections().collections
        collection_names = [col.name for col in collections]
        
        if config.COLLECTION_NAME not in collection_names:
            logger.info(f"Creando colección: {config.COLLECTION_NAME}")
            self.client.create_collection(
                collection_name=config.COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=config.EMBEDDING_DIMENSION,
                    distance=Distance.COSINE
                )
            )
        else:
            logger.info(f"Colección '{config.COLLECTION_NAME}' ya existe")
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        
        """Generar embeddings para una lista de textos"""

        embeddings = self.embedding_model.encode(
            texts,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        return embeddings.tolist()
    
    def add_documents(self, documents: List[Dict], chunk_size: int = config.CHUNK_SIZE):

        """
        Agregar documentos a Qdrant
        documents: lista de diccionarios con 'content' y 'metadata'
        """

        from document_loader import DocumentLoader
        
        loader = DocumentLoader(config.DOCUMENTS_PATH)
        
        all_chunks = []
        all_metadatas = []
        
        chunk_counter = 0
        
        for doc in documents:
            # Dividir en chunks
            chunks = loader.chunk_text(doc['content'], chunk_size=chunk_size, overlap=config.CHUNK_OVERLAP)
            
            for i, chunk in enumerate(chunks):
                all_chunks.append(chunk)
                all_metadatas.append({
                    **doc['metadata'],
                    'chunk_index': i,
                    'text': chunk  # Qdrant permite guardar el texto también
                })
                chunk_counter += 1
        
        logger.info(f"\nGenerando embeddings para {chunk_counter} chunks...")
        embeddings = self.embed_texts(all_chunks)
        
        logger.info(f"Guardando en Qdrant...")
        
        # Preparar puntos para Qdrant
        points = []
        for idx, (embedding, metadata) in enumerate(zip(embeddings, all_metadatas)):
            point_id = str(uuid.uuid4())  # ID único
            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=metadata
                )
            )
        
        # Insertar en batch
        self.client.upsert(
            collection_name=config.COLLECTION_NAME,
            points=points
        )
        
        logger.info(f"{chunk_counter} chunks indexados exitosamente")
    
    def search(self, query: str, top_k: int = config.TOP_K_RESULTS) -> List[Dict]:

        """
        Buscar documentos similares a la query
        Retorna lista de diccionarios con 'content' y 'metadata'
        """

        # Generar embedding de la query
        query_embedding = self.embed_texts([query])[0]
                
        results = self.client.query_points(
            collection_name=config.COLLECTION_NAME,
            query=query_embedding,
            limit=top_k
        )
        
        # Formatear resultados
        retrieved_docs = []
        for point in results.points:
            retrieved_docs.append({
                'content': point.payload.get('text', ''),
                'metadata': {
                    'source': point.payload.get('source', ''),
                    'type': point.payload.get('type', ''),
                    'chunk_index': point.payload.get('chunk_index', 0)
                },
                'score': point.score  # Score de similitud
            })
        
        return retrieved_docs
    
    def count_documents(self) -> int:

        """Contar documentos en la colección"""

        collection_info = self.client.get_collection(config.COLLECTION_NAME)
        return collection_info.points_count
    
    def reset_collection(self):

        """
        Eliminar y recrear la colección desde cero
        En modo embebido, elimina físicamente el storage
        """

        try:
            if self.embedded_mode:
                logger.info("Realizando reset físico...")
                
                # Cerrar cliente actual
                self.client.close()
                logger.info("Cliente Qdrant cerrado")
                
                # Tiempo para que el SO libere los archivos
                time.sleep(0.5)
                
                # Eliminar físicamente el directorio de storage
                if os.path.exists(config.QDRANT_PATH):
                    shutil.rmtree(config.QDRANT_PATH)
                    logger.info(f"Storage físico eliminado: {config.QDRANT_PATH}")
                
                # Recrear el cliente (esto recreará el directorio)
                self.client = QdrantClient(path=config.QDRANT_PATH)
                logger.info("Cliente Qdrant reinicializado")
                
                # Crear colección limpia
                self._create_collection_if_not_exists()
                logger.info("Colección recreada desde cero")
                
            else:
                # Modo cliente-servidor: solo eliminar colección
                logger.info("Eliminando colección...")
                try:
                    self.client.delete_collection(config.COLLECTION_NAME)
                    logger.info(f"Colección '{config.COLLECTION_NAME}' eliminada")
                except Exception as e:
                    logger.info(f"No se pudo eliminar la colección: {e}")
                
                self._create_collection_if_not_exists()
                logger.info("Colección recreada")
                
        except Exception as e:
            logger.info(f"Error durante el reset: {e}")
            raise
        
        logger.info("Reset completado exitosamente")
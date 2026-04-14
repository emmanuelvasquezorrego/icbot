#!/usr/bin/env python3
"""
Script para indexar documentos en Qdrant
"""

import os
import sys
from document_loader import DocumentLoader
from vector_store import VectorStore
import config


def main():
    print("=" * 60)
    print("INDEXADOR DE DOCUMENTOS - Sistema RAG con Qdrant")
    print("=" * 60)
    
    # Verificar que existe el directorio de documentos
    if not os.path.exists(config.DOCUMENTS_PATH):
        print(f"\n✗ Error: No existe el directorio '{config.DOCUMENTS_PATH}'")
        print(f"  Crea el directorio y coloca archivos TXT o PDF ahí")
        print(f"  Comando: mkdir {config.DOCUMENTS_PATH}")
        sys.exit(1)
    
    # Verificar que hay archivos
    files = [f for f in os.listdir(config.DOCUMENTS_PATH) 
             if f.endswith(('.txt', '.pdf'))]
    
    if not files:
        print(f"\nError: No hay archivos TXT o PDF en '{config.DOCUMENTS_PATH}'")
        print(f"  Coloca al menos un archivo .txt o .pdf en ese directorio")
        sys.exit(1)
    
    print(f"\nArchivos encontrados:")
    for f in files:
        print(f"  - {f}")
    
    # Preguntar si reiniciar la base de datos
    print("\n¿Desea reiniciar la base de datos? (s/n): ", end="")
    reset = input().strip().lower()
    
    # Inicializar vector store
    print("\nInicializando Qdrant...")
    vector_store = VectorStore()
    
    if reset == 's':
        print("\nReiniciando base de datos...")
        vector_store.reset_collection()
    else:
        count = vector_store.count_documents()
        print(f"\nBase de datos actual: {count} chunks indexados")
    
    # Cargar documentos
    print(f"\nCargando documentos desde '{config.DOCUMENTS_PATH}'...")
    loader = DocumentLoader(config.DOCUMENTS_PATH)
    documents = loader.load_all_documents()
    
    if not documents:
        print("\nNo se pudieron cargar documentos")
        sys.exit(1)
    
    print(f"\n{len(documents)} documentos cargados correctamente")
    
    # Indexar en Qdrant
    print("\nIndexando documentos en Qdrant...")
    print("(Esto puede tomar unos momentos...)")
    
    try:
        vector_store.add_documents(documents)
        
        # Mostrar resumen
        total_count = vector_store.count_documents()
        print("\n" + "=" * 60)
        print(f"INDEXACIÓN COMPLETADA")
        print(f"  Total de chunks en la base de datos: {total_count}")
        print(f"  Ubicación: {config.QDRANT_PATH if config.QDRANT_PATH else f'{config.QDRANT_HOST}:{config.QDRANT_PORT}'}")
        print("=" * 60)
        print("\nYa puede ejecutar el chatbot con:")
        print("  python chat.py")
        
    except Exception as e:
        print(f"\nError durante la indexación: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
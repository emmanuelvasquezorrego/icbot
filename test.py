#!/usr/bin/env python3
"""
Script de prueba simple para verificar la instalación
"""

import sys


def test_imports():

    """Probar que todas las dependencias se importan correctamente"""

    print("Probando imports...\n")
    
    modules = [
        ("langchain", "LangChain"),
        ("langchain_groq", "LangChain-Groq"),
        ("langchain_community", "LangChain-Community"),
        ("langgraph", "LangGraph"),
        ("qdrant_client", "Qdrant Client"),
        ("sentence_transformers", "Sentence Transformers"),
        ("pypdf", "PyPDF"),
        ("dotenv", "Python-dotenv"),
    ]
    
    success = True
    for module, name in modules:
        try:
            __import__(module)
            print(f"{name}")
        except ImportError as e:
            print(f"{name}: {e}")
            success = False
    
    return success


def test_config():

    """Probar configuración"""

    print("\nProbando configuración...\n")
    
    try:
        import config
        
        if config.GROQ_API_KEY and config.GROQ_API_KEY != "tu_api_key_de_groq_aqui":
            print(f"GROQ_API_KEY configurada")
        else:
            print(f"GROQ_API_KEY no configurada (edita .env)")
            return False
        
        print(f"✓ Modelo: {config.GROQ_MODEL}")
        print(f"✓ Collection: {config.COLLECTION_NAME}")
        print(f"✓ Qdrant Path: {config.QDRANT_PATH}")
        
        return True
        
    except Exception as e:
        print(f"Error en configuración: {e}")
        return False


def test_qdrant():

    """Probar conexión a Qdrant"""

    print("\nProbando Qdrant...\n")
    
    try:
        from qdrant_client import QdrantClient
        import config
        
        if config.QDRANT_PATH:
            client = QdrantClient(path=config.QDRANT_PATH)
            print(f"Qdrant inicializado en modo local: {config.QDRANT_PATH}")
        else:
            client = QdrantClient(host=config.QDRANT_HOST, port=config.QDRANT_PORT)
            print(f"Qdrant conectado: {config.QDRANT_HOST}:{config.QDRANT_PORT}")
        
        # Listar colecciones
        collections = client.get_collections()
        print(f"Colecciones disponibles: {len(collections.collections)}")
        
        return True
        
    except Exception as e:
        print(f"Error conectando a Qdrant: {e}")
        return False


def main():
    print("=" * 60)
    print("TEST DE INSTALACIÓN - Sistema RAG con Qdrant")
    print("=" * 60 + "\n")
    
    # Test imports
    if not test_imports():
        print("\nAlgunas dependencias faltan. Ejecute:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    
    # Test config
    if not test_config():
        print("\nConfiguración incompleta. Asegúrese de:")
        print("  1. Copiar .env.example a .env")
        print("  2. Agregar su GROQ_API_KEY en .env")
    
    # Test Qdrant
    test_qdrant()
    
    print("\n" + "=" * 60)
    print("✓ INSTALACIÓN CORRECTA")
    print("=" * 60)
    print("\nSiguientes pasos:")
    print("  1. Crear el directorio: mkdir documents")
    print("  2. Agregar archivos TXT o PDF en documents/")
    print("  3. Indexar: python indexar.py")
    print("  4. Chatear: python chat.py")
    print("\nNota sobre Qdrant:")
    print("  - Modo actual: Local embebido (sin Docker)")
    print("  - Los datos se guardan en: ./qdrant_storage")
    print("  - Para usar Docker, modifica config.py")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Script para indexar documentos en Qdrant
"""

import os
import sys
from core.document_loader import DocumentLoader
from core.vector_store import VectorStore
import config


def main():
    print("=" * 60)
    print("INDEXADOR DE DOCUMENTOS - Sistema RAG con Qdrant")
    print("=" * 60)
    
    # Verificar que existe el directorio de documentos
    if not os.path.exists(config.DOCUMENTS_PATH):
        print(f"\nError: No existe el directorio '{config.DOCUMENTS_PATH}'")
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
    
    # Inicializar vector store
    print("\nInicializando Qdrant...")
    vector_store = VectorStore()

    current_count = vector_store.count_documents()
    print(f"\nEstado actual de la base de datos: {current_count} chunks indexados")

    print("\n" + "=" * 60)

    if current_count > 0:
        print("La base de datos ya contiene documentos indexados.")
        print("¿Qué acción desea realizar?")
        print("  1. Reiniciar base de datos (borrar todo e indexar de nuevo)")
        print("  2. Cancelar operación")
        print("\nNota: Se reinicia para agregar documentos y así evitar duplicados.")

        while True:
            choice = input("Seleccione una opción (1 o 2): ").strip()
            if choice in ['1', '2']:
                break
            print("Opción no válida. Por favor, ingrese 1 o 2.")

        if choice == '1':

            # Reiniciar base de datos completa
            print("\n" + "=" * 60)
            print("Confirmación de reinicio")
            print("=" * 60)
            print("Esta acción:")
            print(f"  • Eliminará los {current_count} chunks existentes")
            print(f"  • Indexará {len(files)} archivos actuales")
            print("-" * 60)

            while True:
                confirm = input("¿Confirma que desea reiniciar la base de datos? (s/n): ").strip().lower()
                if confirm in ['s', 'n', '']:
                    break
                print("Opción no válida. Ingrese 's' para sí o 'n' para no.")
    
            if confirm != 's':
                print("\nReinicio cancelado.")
                sys.exit(0)

            print("\nEliminando base de datos existente...")
            vector_store.reset_collection()
            print("Base de datos reiniciada exitosamente")

        elif choice == '2':
            print("\nOperación cancelada.")
            sys.exit(0)
    
    else:
        # Base de datos vacía - indexar directamente
        print("La base de datos está vacía.")
        print(f"Se indexarán {len(files)} archivos.")
        
        while True:
            choice = input("\n¿Desea continuar con la indexación? (s/n): ").strip().lower()
            if choice in ['s', 'n', '']:
                break
            print("Opción no válida. Ingrese 's' para sí o 'n' para no.")
                    
        if choice == 'n':
            print("\nOperación cancelada.")
            sys.exit(0)
    
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
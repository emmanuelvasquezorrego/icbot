#!/usr/bin/env python3
"""
Script para ejecutar el chatbot RAG en consola
"""

import sys
from rag_agent import RAGAgent
from vector_store import VectorStore


def print_banner():

    print("\n" + "=" * 60)
    print(" CHATBOT RAG LOCAL - Qdrant + Groq + LangGraph")
    print("=" * 60)
    print("\nComandos disponibles:")
    print("  - Escribe tu pregunta y presiona Enter")
    print("  - 'salir' o 'exit' para terminar")
    print("  - 'limpiar' para limpiar la pantalla")
    print("=" * 60)


def check_database():

    """Verificar que la base de datos tiene documentos"""

    vector_store = VectorStore()
    count = vector_store.count_documents()
    
    if count == 0:
        print("\nADVERTENCIA: La base de datos está vacía")
        print("  Ejecuta primero: python indexar.py")
        print("\n¿Desea continuar de todos modos? (s/n): ", end="")
        response = input().strip().lower()
        if response != 's':
            sys.exit(0)
    else:
        print(f"\nBase de datos lista: {count} chunks indexados")


def main():
    print_banner()
    
    # Verificar base de datos
    check_database()
    
    # Inicializar agente
    print("\nInicializando agente RAG...")
    try:
        agent = RAGAgent()
        print("Agente listo\n")
    except Exception as e:
        print(f"\nError inicializando el agente: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Loop principal
    print("Puede empezar a hacer preguntas:\n")
    
    while True:
        try:
            # Obtener pregunta del usuario
            print("Tu pregunta: ", end="")
            question = input().strip()
            
            # Verificar comandos especiales
            if question.lower() in ['salir', 'exit', 'quit']:
                print("\nHasta luego\n")
                break
            
            if question.lower() in ['limpiar', 'clear', 'cls']:
                import os
                os.system('clear' if os.name == 'posix' else 'cls')
                print_banner()
                continue
            
            if not question:
                continue
            
            # Procesar pregunta
            print()
            answer = agent.query(question)
            
            # Mostrar respuesta
            print(f"\nRespuesta:\n{answer}\n")
            print("-" * 60 + "\n")
            
        except KeyboardInterrupt:
            print("\n\nHasta luego\n")
            break
        except Exception as e:
            print(f"\nError: {e}\n")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
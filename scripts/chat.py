#!/usr/bin/env python3
"""
Script para probar el agente RAG desde la terminal.
Solo para desarrollo local — en producción usar Docker.
"""

import sys
from core.rag_agent import RAGAgent
from core.vector_store import VectorStore


def print_banner():
    print("\n" + "=" * 60)
    print(" CHATBOT RAG LOCAL - Qdrant + Groq + LangGraph")
    print("=" * 60)
    print(" Comandos:")
    print("   'salir'   → terminar sesión")
    print("   'limpiar' → borrar historial de conversación")
    print("=" * 60)


def check_database() -> bool:
    """Verificar que la base de datos tiene documentos."""
    vs = VectorStore()
    count = vs.count_documents()

    if count == 0:
        print("\n⚠  Base de datos vacía.")
        print("   Ejecuta primero: python indexar.py")
        respuesta = input("\n¿Continuar de todos modos? (s/n): ").strip().lower()
        return respuesta == "s"

    print(f"\n✓ Base de datos lista: {count} chunks indexados")
    return True


def main():
    print_banner()

    if not check_database():
        sys.exit(0)

    PHONE_LOCAL = "local_test"

    print("\nInicializando agente RAG...")
    try:
        agent = RAGAgent()
        print("✓ Agente listo\n")
    except Exception as e:
        print(f"\n✗ Error inicializando el agente: {e}")
        sys.exit(1)

    print("Puede empezar a hacer preguntas:\n")

    while True:
        try:
            question = input("Pregunta: ").strip()

            if not question:
                continue

            if question.lower() in ("salir", "exit", "quit"):
                print("\nHasta luego\n")
                break

            if question.lower() in ("limpiar", "clear"):
                if agent.conversation_manager:
                    agent.conversation_manager.clear_history(PHONE_LOCAL)
                    print("✓ Historial limpiado\n")
                continue

            answer, docs = agent.query(
                phone=PHONE_LOCAL,
                question=question
            )

            print(f"\nRespuesta:\n{answer}")

            if docs:
                print(f"\nFuentes ({len(docs)}):")
                for d in docs:
                    print(
                        f"  - {d['metadata']['source']} "
                        f"(score: {d['score']:.3f})"
                    )

            print("-" * 60 + "\n")

        except KeyboardInterrupt:
            print("\n\nHasta luego\n")
            break
        except Exception as e:
            print(f"\n✗ Error: {e}\n")


if __name__ == "__main__":
    main()
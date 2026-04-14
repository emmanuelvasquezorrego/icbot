"""
Agente RAG con LangGraph
"""

from typing import TypedDict, Sequence
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from vector_store import VectorStore
import config


# Definir el estado del agente
class AgentState(TypedDict):

    """Estado del agente RAG"""

    question: str
    retrieved_context: list
    answer: str
    messages: Sequence[HumanMessage | AIMessage | SystemMessage]


class RAGAgent:

    """Agente RAG con LangGraph"""
    
    def __init__(self):
        # Inicializar LLM de Groq
        self.llm = ChatGroq(
            api_key=config.GROQ_API_KEY,
            model_name=config.GROQ_MODEL,
            temperature=0.3
        )
        
        # Inicializar Vector Store
        self.vector_store = VectorStore()
        
        # Construir el grafo
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:

        """Construir el grafo de LangGraph"""
        
        # Crear el grafo
        workflow = StateGraph(AgentState)
        
        # Agregar nodos
        workflow.add_node("user_input", self.process_user_input)
        workflow.add_node("retrieve_documents", self.retrieve_documents)
        workflow.add_node("generate_answer", self.generate_answer)
        workflow.add_node("respond_output", self.respond_output)
        
        # Definir edges
        workflow.set_entry_point("user_input")
        workflow.add_edge("user_input", "retrieve_documents")
        workflow.add_edge("retrieve_documents", "generate_answer")
        workflow.add_edge("generate_answer", "respond_output")
        workflow.add_edge("respond_output", END)
        
        # Compilar el grafo
        return workflow.compile()
    
    def process_user_input(self, state: AgentState) -> AgentState:

        """Nodo 1: Procesar entrada del usuario"""

        print("\n[NODO] Procesando entrada del usuario...")
        return state
    
    def retrieve_documents(self, state: AgentState) -> AgentState:

        """Nodo 2: Recuperar documentos relevantes"""

        print("[NODO] Recuperando documentos relevantes...")
        
        question = state["question"]
        
        # Buscar en la base de conocimiento
        retrieved_docs = self.vector_store.search(
            query=question,
            top_k=config.TOP_K_RESULTS
        )
        
        state["retrieved_context"] = retrieved_docs
        
        if retrieved_docs:
            print(f"Se encontraron {len(retrieved_docs)} documentos relevantes")
            for i, doc in enumerate(retrieved_docs):
                print(f"  - Doc {i+1}: Score {doc.get('score', 0):.3f} | Fuente: {doc['metadata']['source']}")
        else:
            print("No se encontraron documentos relevantes")
        
        return state
    
    def generate_answer(self, state: AgentState) -> AgentState:

        """Nodo 3: Generar respuesta usando LLM"""

        print("[NODO] Generando respuesta...")
        
        question = state["question"]
        context_docs = state["retrieved_context"]
        
        # Construir contexto
        if context_docs:
            context = "\n\n".join([
                f"Fragmento {i+1} (Fuente: {doc['metadata']['source']}, Score: {doc.get('score', 0):.3f}):\n{doc['content']}"
                for i, doc in enumerate(context_docs)
            ])
        else:
            context = "No se encontró información relevante en la base de conocimiento."
        
        # Crear prompt
        system_prompt = """Eres un asistente útil que responde preguntas basándose ÚNICAMENTE en el contexto proporcionado.

REGLAS IMPORTANTES:
1. Si la información está en el contexto, úsala para responder
2. Si la información NO está en el contexto, di claramente: "No tengo información sobre eso en mi base de conocimiento"
3. NO inventes información
4. NO uses conocimiento general si no está en el contexto
5. Sé conciso y directo
6. Cita la fuente cuando sea relevante"""
        
        user_prompt = f"""Contexto:
{context}

Pregunta: {question}

Respuesta:"""
        
        # Generar respuesta
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = self.llm.invoke(messages)
        state["answer"] = response.content
        
        return state
    
    def respond_output(self, state: AgentState) -> AgentState:

        """Nodo 4: Preparar salida final"""

        print("[NODO] Preparando respuesta final...")
        return state
    
    def query(self, question: str) -> str:

        """
        Procesar una pregunta y retornar respuesta
        """
        
        # Estado inicial
        initial_state = {
            "question": question,
            "retrieved_context": [],
            "answer": "",
            "messages": []
        }
        
        # Ejecutar el grafo
        final_state = self.graph.invoke(initial_state)
        
        return final_state["answer"]
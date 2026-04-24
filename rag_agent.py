"""
Agente RAG con LangGraph
"""

from typing import TypedDict, Sequence
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from vector_store import VectorStore
import config
import json

# Definir el estado del agente
class AgentState(TypedDict):

    """Estado del agente RAG"""

    phone: str
    question: str
    resolved_question: str
    retrieved_context: list
    answer: str
    messages: Sequence[HumanMessage | AIMessage | SystemMessage]
    conversation_topic: str


class RAGAgent:

    """Agente RAG con LangGraph"""
    
    def __init__(self, conversation_manager=None):
        # Inicializar LLM de Groq
        self.llm = ChatGroq(
            api_key=config.GROQ_API_KEY,
            model_name=config.GROQ_MODEL,
            temperature=0.3
        )

        # LLM rápido para resolver contexto
        self.llm_fast = ChatGroq(
            api_key=config.GROQ_API_KEY,
            model_name=config.GROQ_MODEL_FAST,
            temperature=0.1
        )

        # Inicializar Vector Store
        self.vector_store = VectorStore()

        # Conversation Manager (para mantener el historial de conversaciones)
        self.conversation_manager = conversation_manager
        
        # Construir el grafo
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:

        """Construir el grafo de LangGraph"""
        
        # Crear el grafo
        workflow = StateGraph(AgentState)
        
        # Agregar nodos
        workflow.add_node("resolve_context", self.resolve_context) 
        workflow.add_node("retrieve_documents", self.retrieve_documents)
        workflow.add_node("generate_answer", self.generate_answer)
        
        # Definir edges
        workflow.set_entry_point("resolve_context")
        workflow.add_edge("resolve_context", "retrieve_documents")
        workflow.add_edge("retrieve_documents", "generate_answer")
        workflow.add_edge("generate_answer", END)
        
        # Compilar el grafo
        return workflow.compile()
    
    def resolve_context(self, state: AgentState) -> AgentState:

        """Nodo 1: Resolver contexto usando historial de conversación"""

        print("\n[NODO] Procesando entrada del usuario...")

        question = state["question"]
        phone = state.get("phone", "")
        
        # Obtener historial del ConversationManager
        context_string = ""
        if self.conversation_manager and phone:
            context_string = self.conversation_manager.get_context_string(
                phone, 
                limit=config.MAX_CONTEXT_MESSAGES
            )
        
        if not context_string:
            state["resolved_question"] = question
            state["conversation_topic"] = ""
            return state
        
        # Prompt para resolver referencias
        resolve_prompt = f"""Eres un asistente que resuelve referencias en preguntas.

CONVERSACIÓN PREVIA:
{context_string}

PREGUNTA ACTUAL: "{question}"

TAREA: Reescribe la pregunta para que sea COMPLETA y AUTOCONTENIDA.

Ejemplo:
- Conversación: "¿Hay piscina?" → "Sí, hay piscina"
  Pregunta: "¿En qué horarios abre?"
  Respuesta: "¿En qué horarios abre la piscina?"

Responde SOLO con un JSON:
{{"resolved": "pregunta completa", "topic": "tema principal"}}"""
        
        try:
            response = self.llm_fast.invoke([HumanMessage(content=resolve_prompt)])
            content = response.content.strip()
            
            # Limpiar markdown
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            
            result = json.loads(content)
            state["resolved_question"] = result.get("resolved", question)
            state["conversation_topic"] = result.get("topic", "")
            
            print(f"  Original: {question}")
            print(f"  Resuelta: {state['resolved_question']}")
            
        except Exception as e:
            print(f"  Error: {e}, usando pregunta original")
            state["resolved_question"] = question
            state["conversation_topic"] = ""
        
        return state
    
    def retrieve_documents(self, state: AgentState) -> AgentState:

        """Nodo 2: Recuperar documentos relevantes"""

        print("[NODO] Recuperando documentos relevantes...")
        
        search_query = state["resolved_question"]
        topic = state.get("conversation_topic", "")
        
        # Si el LLM identificó un tema, se agrega a la consulta de búsqueda para mejorar resultados
        if topic and topic.lower() not in search_query.lower():
            search_query = f"{topic} {search_query}"
        
        print(f"  Buscando: {search_query}")
        
        retrieved_docs = self.vector_store.search(
            query=search_query,
            top_k=config.TOP_K_RESULTS
        )
        
        state["retrieved_context"] = retrieved_docs
        print(f"  Encontrados: {len(retrieved_docs)} documentos")
        
        return state
    
    def generate_answer(self, state: AgentState) -> AgentState:

        """Nodo 3: Generar respuesta usando LLM"""

        print("[NODO] Generando respuesta...")
        
        phone = state.get("phone", "")
        question = state["question"]
        resolved = state["resolved_question"]
        topic = state.get("conversation_topic", "")
        docs = state["retrieved_context"]
        
        # Obtener historial
        history_text = ""
        if self.conversation_manager and phone:
            history_text = self.conversation_manager.get_context_string(
                phone,
                limit=config.MAX_CONTEXT_MESSAGES
            )
        
        # Contexto de documentos
        if docs:
            context_text = "\n\n".join([
                f"[Doc {i+1}: {d['metadata']['source']}]\n{d['content']}"
                for i, d in enumerate(docs)
            ])
        else:
            context_text = "No hay información en documentos"
        
        # Prompt para generar respuesta
        system_prompt = f"""Eres un asistente para un conjunto residencial.

⚠️ REGLAS CRÍTICAS:
1. USA EL HISTORIAL para mantener contexto
2. Responde de forma DIRECTA y CONCISA
3. Ve al grano, sin introducciones ni rodeos
4. NO ofrezcas información adicional a menos que el usuario pregunte
5. Si no tienes un dato específico, di solo: "No tengo información sobre eso"
6. NO sugieras contactar a administración a menos que sea indispensable
7. NO hagas preguntas al final (como "¿Quieres saber más?")

Tema actual: {topic if topic else 'general'}"""
        
        # Prompt para el usuario
        user_prompt = f"""## HISTORIAL DE CONVERSACIÓN:
{history_text if history_text else "Sin historial previo"}

## INFORMACIÓN DE DOCUMENTOS:
{context_text}

## PREGUNTA ORIGINAL: {question}
## PREGUNTA CON CONTEXTO: {resolved}

Responde de manera natural y conversacional:"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = self.llm.invoke(messages)
        state["answer"] = response.content
        
        return state
    
    def query(self, phone: str, question: str) -> tuple[str, list]:

        """
        Ejecuta el grafo completo para una pregunta dada.
        Retorna la respuesta generada y los documentos recuperados.
        """
        
        initial_state = {
            "phone": phone,
            "question": question,
            "resolved_question": question,
            "retrieved_context": [],
            "answer": "",
            "messages": [],
            "conversation_topic": ""
        }
        
        final_state = self.graph.invoke(initial_state)
        
        # Guardar en el ConversationManager
        if self.conversation_manager:
            self.conversation_manager.add_message(phone, "user", question)
            self.conversation_manager.add_message(phone, "assistant", final_state["answer"])
        
        return final_state["answer"], final_state["retrieved_context"]
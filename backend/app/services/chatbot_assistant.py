"""
AI Chatbot Assistant for Blast Furnace Analytics
Implements intent classification, RAG patterns, and conversation management using Gemini 1.5 Flash API
"""

import os
import json
import google.generativeai as genai
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import pandas as pd
import numpy as np


class IntentType(str, Enum):
    """Supported intent types for the chatbot"""
    DATA_QUERY = "data_query"
    ANALYTICS_REQUEST = "analytics_request"
    ANOMALY_INVESTIGATION = "anomaly_investigation"
    FORECAST_REQUEST = "forecast_request"
    EXPLANATION_REQUEST = "explanation_request"
    COMPARISON_REQUEST = "comparison_request"
    TREND_ANALYSIS = "trend_analysis"
    ROOT_CAUSE_INQUIRY = "root_cause_inquiry"
    GENERAL_QUESTION = "general_question"
    GREETING = "greeting"
    FAREWELL = "farewell"
    UNKNOWN = "unknown"


@dataclass
class Message:
    """Represents a chat message"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationContext:
    """Maintains conversation context and history"""
    session_id: str
    messages: List[Message] = field(default_factory=list)
    current_intent: IntentType = IntentType.UNKNOWN
    entities: Dict[str, Any] = field(default_factory=dict)
    last_query_params: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class IntentResult:
    """Result of intent classification"""
    intent: IntentType
    confidence: float
    entities: Dict[str, Any]
    suggested_parameters: Dict[str, Any]


class IntentClassifier:
    """Classifies user queries into predefined intents using Gemini"""

    def __init__(self, model: Any):
        self.model = model
        self.intent_examples = self._load_intent_examples()

    def _load_intent_examples(self) -> Dict[IntentType, List[str]]:
        """Load example queries for each intent type"""
        return {
            IntentType.DATA_QUERY: [
                "Show me the hot metal temperature from yesterday",
                "What was the silicon content last week?",
                "Get me the pressure readings for furnace 1",
                "Display the coke rate for the last 24 hours"
            ],
            IntentType.ANALYTICS_REQUEST: [
                "Run SPC analysis on hot metal temperature",
                "Generate correlation matrix for all parameters",
                "Perform root cause analysis on the anomaly",
                "Create analytics report for this week"
            ],
            IntentType.ANOMALY_INVESTIGATION: [
                "Why did the temperature spike at 3 PM?",
                "Investigate the pressure drop this morning",
                "What caused the silicon deviation yesterday?",
                "Explain the anomaly in coke rate"
            ],
            IntentType.FORECAST_REQUEST: [
                "Predict hot metal temperature for next 12 hours",
                "Forecast silicon content for tomorrow",
                "What will be the pressure trend next week?",
                "Generate 24-hour forecast for all parameters"
            ],
            IntentType.EXPLANATION_REQUEST: [
                "Explain what SPC means",
                "How is Cpk calculated?",
                "What does a negative correlation indicate?",
                "Tell me about blast furnace operations"
            ],
            IntentType.COMPARISON_REQUEST: [
                "Compare this week's performance with last week",
                "Show me the difference between furnace 1 and 2",
                "Compare actual vs predicted values",
                "How does today's output compare to the target?"
            ],
            IntentType.TREND_ANALYSIS: [
                "Show me the trend for hot metal temperature",
                "Is the silicon content increasing or decreasing?",
                "Analyze the pressure trend over the month",
                "What's the long-term trend for coke rate?"
            ],
            IntentType.ROOT_CAUSE_INQUIRY: [
                "What's causing the high temperature?",
                "Identify factors affecting silicon content",
                "Root cause of pressure fluctuations",
                "Why is the efficiency dropping?"
            ],
            IntentType.GENERAL_QUESTION: [
                "How many parameters are being monitored?",
                "What's the current status of the furnace?",
                "Give me a summary of today's operations",
                "What alerts are currently active?"
            ],
            IntentType.GREETING: [
                "Hello",
                "Hi there",
                "Good morning",
                "Hey"
            ],
            IntentType.FAREWELL: [
                "Goodbye",
                "See you later",
                "Thanks, that's all",
                "Bye"
            ]
        }

    def classify(self, query: str) -> IntentResult:
        """
        Classify user query into an intent.

        Args:
            query: User's input query

        Returns:
            IntentResult with classified intent and extracted entities
        """
        # Build prompt for intent classification
        examples_text = ""
        for intent_type, examples in self.intent_examples.items():
            for example in examples[:3]:  # Use first 3 examples per intent
                examples_text += f"- \"{example}\" -> {intent_type.value}\n"

        prompt = f"""
        You are an intent classifier for a blast furnace analytics chatbot.
        Classify the following user query into one of these intents:
        {', '.join([i.value for i in IntentType])}

        Examples:
        {examples_text}

        User query: "{query}"

        Respond ONLY with a JSON object in this format:
        {{
            "intent": "<intent_type>",
            "confidence": <0.0-1.0>,
            "entities": {{
                "parameters": [],
                "time_range": null,
                "furnace_id": null,
                "metrics": []
            }}
        }}

        Extract any mentioned parameters (like temperature, pressure, silicon),
        time ranges (yesterday, last week, last 24 hours), furnace IDs, and specific metrics.
        """

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()

            # Parse JSON response
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            result_dict = json.loads(response_text.strip())

            return IntentResult(
                intent=IntentType(result_dict.get("intent", "unknown")),
                confidence=result_dict.get("confidence", 0.5),
                entities=result_dict.get("entities", {}),
                suggested_parameters={}
            )
        except Exception as e:
            # Fallback to keyword-based classification
            return self._keyword_classification(query)

    def _keyword_classification(self, query: str) -> IntentResult:
        """Fallback keyword-based intent classification"""
        query_lower = query.lower()

        keywords_map = {
            IntentType.DATA_QUERY: ["show", "get", "display", "what was", "retrieve"],
            IntentType.ANALYTICS_REQUEST: ["analyze", "run analysis", "generate report", "correlation", "spc"],
            IntentType.ANOMALY_INVESTIGATION: ["why did", "investigate", "caused", "spike", "drop", "anomaly"],
            IntentType.FORECAST_REQUEST: ["predict", "forecast", "will be", "next", "future"],
            IntentType.EXPLANATION_REQUEST: ["explain", "what is", "how does", "tell me about"],
            IntentType.COMPARISON_REQUEST: ["compare", "difference", "vs", "versus"],
            IntentType.TREND_ANALYSIS: ["trend", "increasing", "decreasing", "pattern"],
            IntentType.ROOT_CAUSE_INQUIRY: ["root cause", "causing", "factors affecting", "why is"],
            IntentType.GREETING: ["hello", "hi", "good morning", "hey"],
            IntentType.FAREWELL: ["goodbye", "bye", "see you"]
        }

        best_intent = IntentType.UNKNOWN
        best_score = 0

        for intent, keywords in keywords_map.items():
            score = sum(1 for kw in keywords if kw in query_lower)
            if score > best_score:
                best_score = score
                best_intent = intent

        # Extract simple entities
        entities = {
            "parameters": [],
            "time_range": None,
            "furnace_id": None
        }

        # Simple parameter extraction
        param_keywords = ["temperature", "pressure", "silicon", "coke", "hot metal"]
        entities["parameters"] = [p for p in param_keywords if p in query_lower]

        # Simple time range extraction
        time_keywords = ["yesterday", "last week", "last 24 hours", "today", "this week"]
        for tk in time_keywords:
            if tk in query_lower:
                entities["time_range"] = tk
                break

        return IntentResult(
            intent=best_intent,
            confidence=min(best_score * 0.3, 0.9),
            entities=entities,
            suggested_parameters={}
        )


class RAGRetriever:
    """Retrieval-Augmented Generation component for fetching relevant context"""

    def __init__(self, data_store: Optional[Dict[str, Any]] = None):
        self.data_store = data_store or {}
        self.knowledge_base = self._initialize_knowledge_base()

    def _initialize_knowledge_base(self) -> Dict[str, str]:
        """Initialize domain knowledge base"""
        return {
            "spc": """Statistical Process Control (SPC) is a method of quality control which employs statistical methods 
            to monitor and control a process. Key metrics include:
            - Mean (average value)
            - Standard Deviation (variability)
            - Control Limits (UCL/LCL at ±3 sigma)
            - Process Capability (Cp, Cpk)""",

            "cpk": """Cpk (Process Capability Index) measures how well a process can produce output within specification limits.
            - Cpk > 1.33: Capable process
            - Cpk = 1.0: Barely capable
            - Cpk < 1.0: Not capable
            Formula: Cpk = min((USL - μ) / 3σ, (μ - LSL) / 3σ)""",

            "correlation": """Correlation measures the relationship between two variables:
            - Positive correlation: Both variables move in same direction
            - Negative correlation: Variables move in opposite directions
            - Correlation coefficient (r): Ranges from -1 to +1
            - r > 0.7: Strong correlation
            - r > 0.5: Moderate correlation
            - r < 0.3: Weak correlation""",

            "blast_furnace": """A blast furnace is a type of metallurgical furnace used for smelting to produce industrial metals.
            Key parameters monitored:
            - Hot Metal Temperature (1400-1550°C)
            - Silicon Content (0.3-0.8%)
            - Blast Pressure (3-5 bar)
            - Coke Rate (300-500 kg/ton HM)
            - Top Gas Temperature (150-250°C)""",

            "anomaly_detection": """Anomaly detection identifies unusual patterns that deviate from expected behavior.
            Common rules:
            - Western Electric Rules for control charts
            - Points beyond 3-sigma limits (critical)
            - Trends and shifts in process mean
            - Increased variability""",

            "forecasting": """Time series forecasting predicts future values based on historical patterns.
            Methods include:
            - Statistical models (ARIMA, Exponential Smoothing)
            - Machine Learning (Random Forest, XGBoost)
            - Deep Learning (LSTM, Transformer models)
            - Foundation Models (TimesFM for zero-shot forecasting)"""
        }

    def retrieve(self, query: str, intent: IntentType, top_k: int = 3) -> List[Dict[str, str]]:
        """
        Retrieve relevant context for the query.

        Args:
            query: User's query
            intent: Classified intent
            top_k: Number of relevant documents to retrieve

        Returns:
            List of relevant context documents
        """
        # Simple keyword-based retrieval (can be enhanced with embeddings)
        query_lower = query.lower()
        scored_docs = []

        for topic, content in self.knowledge_base.items():
            score = self._calculate_relevance_score(query_lower, topic, content)
            if score > 0:
                scored_docs.append({
                    "topic": topic,
                    "content": content,
                    "relevance_score": score
                })

        # Sort by relevance and return top_k
        scored_docs.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored_docs[:top_k]

    def _calculate_relevance_score(self, query: str, topic: str, content: str) -> float:
        """Calculate relevance score between query and document"""
        score = 0.0

        # Topic match
        if topic in query:
            score += 0.5

        # Keyword overlap
        query_words = set(query.split())
        content_words = set(content.lower().split())
        overlap = len(query_words.intersection(content_words))
        score += min(overlap * 0.05, 0.5)

        return score

    def get_data_context(
        self,
        parameters: List[str],
        time_range: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Retrieve actual data context from data store"""
        if not self.data_store:
            return None

        # This would query the actual database in production
        # For demo, return mock structure
        return {
            "available_parameters": list(self.data_store.keys()),
            "time_range": time_range or "last_24_hours",
            "sample_size": 1000
        }


class ChatbotAssistant:
    """
    Main chatbot assistant integrating intent classification, RAG, and conversation management
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize chatbot with Gemini API.

        Args:
            api_key: Google API key for Gemini (uses env var if not provided)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "Gemini API key required. Set GEMINI_API_KEY environment variable "
                "or pass api_key parameter."
            )

        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

        # Initialize components
        self.intent_classifier = IntentClassifier(self.model)
        self.rag_retriever = RAGRetriever()

        # Conversation management
        self.conversations: Dict[str, ConversationContext] = {}

        # System prompt
        self.system_prompt = """
        You are an AI assistant for blast furnace operations analytics. Your role is to:
        1. Answer questions about furnace parameters and operations
        2. Explain analytics concepts (SPC, correlation, root cause analysis)
        3. Provide insights from data analysis
        4. Be concise, accurate, and helpful
        5. Use technical terminology appropriately
        6. Admit when you don't know something

        Always prioritize safety and accuracy in your responses.
        """

    def start_conversation(self, session_id: str) -> ConversationContext:
        """Start a new conversation session"""
        context = ConversationContext(session_id=session_id)
        self.conversations[session_id] = context
        return context

    def get_conversation(self, session_id: str) -> Optional[ConversationContext]:
        """Get existing conversation or create new one"""
        if session_id not in self.conversations:
            return self.start_conversation(session_id)
        return self.conversations[session_id]

    def chat(
        self,
        query: str,
        session_id: str,
        data_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process user query and generate response.

        Args:
            query: User's input query
            session_id: Conversation session identifier
            data_context: Optional data context for RAG

        Returns:
            Dictionary with response and metadata
        """
        # Get or create conversation context
        context = self.get_conversation(session_id)

        # Add user message to history
        user_message = Message(role="user", content=query)
        context.messages.append(user_message)

        # Classify intent
        intent_result = self.intent_classifier.classify(query)
        context.current_intent = intent_result.intent
        context.entities = intent_result.entities
        context.updated_at = datetime.now()

        # Retrieve relevant context using RAG
        rag_context = self.rag_retriever.retrieve(
            query=query,
            intent=intent_result.intent,
            top_k=3
        )

        # Build enhanced prompt with context
        enhanced_prompt = self._build_enhanced_prompt(
            query=query,
            intent=intent_result,
            rag_context=rag_context,
            data_context=data_context,
            conversation_history=context.messages[-5:]  # Last 5 messages
        )

        # Generate response using Gemini
        try:
            response = self.model.generate_content(enhanced_prompt)
            assistant_response = response.text.strip()
        except Exception as e:
            assistant_response = f"I apologize, but I encountered an error processing your request: {str(e)}"

        # Add assistant message to history
        assistant_message = Message(
            role="assistant",
            content=assistant_response,
            metadata={
                "intent": intent_result.intent.value,
                "confidence": intent_result.confidence,
                "rag_documents_used": len(rag_context)
            }
        )
        context.messages.append(assistant_message)

        return {
            "response": assistant_response,
            "intent": intent_result.intent.value,
            "confidence": intent_result.confidence,
            "entities": intent_result.entities,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "tokens_used": self._estimate_tokens(query + assistant_response)
        }

    def _build_enhanced_prompt(
        self,
        query: str,
        intent: IntentResult,
        rag_context: List[Dict[str, str]],
        data_context: Optional[Dict[str, Any]],
        conversation_history: List[Message]
    ) -> str:
        """Build enhanced prompt with all context"""
        prompt_parts = [self.system_prompt]

        # Add conversation history
        if conversation_history:
            prompt_parts.append("\nRecent conversation:")
            for msg in conversation_history:
                role = "User" if msg.role == "user" else "Assistant"
                prompt_parts.append(f"{role}: {msg.content}")

        # Add RAG context
        if rag_context:
            prompt_parts.append("\nRelevant information:")
            for doc in rag_context:
                prompt_parts.append(f"\n{doc['topic'].upper()}:")
                prompt_parts.append(doc['content'])

        # Add data context if available
        if data_context:
            prompt_parts.append("\nData context:")
            prompt_parts.append(json.dumps(data_context, indent=2))

        # Add current query with intent guidance
        prompt_parts.append(f"\nCurrent query: {query}")
        prompt_parts.append(f"\nDetected intent: {intent.intent.value}")

        if intent.entities.get("parameters"):
            prompt_parts.append(
                f"\nMentioned parameters: {', '.join(intent.entities['parameters'])}"
            )

        prompt_parts.append(
            "\nProvide a clear, concise, and helpful response based on the context above."
        )

        return "\n".join(prompt_parts)

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)"""
        # Average English word is ~4 characters, average token is ~4 characters
        return len(text.split()) * 1.3

    def get_conversation_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get summary of conversation session"""
        if session_id not in self.conversations:
            return None

        context = self.conversations[session_id]

        return {
            "session_id": session_id,
            "message_count": len(context.messages),
            "created_at": context.created_at.isoformat(),
            "updated_at": context.updated_at.isoformat(),
            "current_intent": context.current_intent.value,
            "entities_discussed": context.entities,
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "metadata": msg.metadata
                }
                for msg in context.messages[-10:]  # Last 10 messages
            ]
        }

    def clear_conversation(self, session_id: str) -> bool:
        """Clear conversation history"""
        if session_id in self.conversations:
            del self.conversations[session_id]
            return True
        return False


# Convenience function for quick testing
def test_chatbot(query: str, session_id: str = "test_session") -> Dict[str, Any]:
    """
    Quick test function for chatbot.

    Args:
        query: Test query
        session_id: Session identifier

    Returns:
        Chatbot response
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {
            "error": "GEMINI_API_KEY not set in environment",
            "response": "Please set GEMINI_API_KEY environment variable to use the chatbot."
        }

    assistant = ChatbotAssistant(api_key=api_key)
    return assistant.chat(query=query, session_id=session_id)


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "Explain what SPC analysis means in blast furnace monitoring"

    print(f"Testing chatbot with query: {query}\n")
    result = test_chatbot(query)

    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Intent: {result['intent']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Response:\n{result['response']}")

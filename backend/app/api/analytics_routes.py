"""
API Routes for Advanced Analytics and Chatbot Assistant
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Import our services
from app.services.analytics_engine import (
    AdvancedAnalyticsEngine,
    quick_analytics
)
from app.services.chatbot_assistant import (
    ChatbotAssistant,
    IntentType
)

router = APIRouter(prefix="/analytics", tags=["Advanced Analytics"])

# Mock data generator for demo purposes
def generate_mock_furnace_data(hours: int = 168) -> pd.DataFrame:
    """Generate mock blast furnace data for testing"""
    np.random.seed(42)
    
    # Create time index
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=hours)
    timestamps = pd.date_range(start=start_time, end=end_time, freq='H')
    
    # Generate realistic furnace parameters
    n = len(timestamps)
    
    # Hot metal temperature (1400-1550°C with some variation)
    base_temp = 1475
    temp_trend = np.linspace(0, 10, n)  # Slight increasing trend
    temp_noise = np.random.normal(0, 15, n)
    temp_seasonal = 5 * np.sin(np.linspace(0, 8*np.pi, n))  # Daily cycles
    hot_metal_temp = base_temp + temp_trend + temp_noise + temp_seasonal
    
    # Silicon content (0.3-0.8%)
    silicon_base = 0.55
    silicon_noise = np.random.normal(0, 0.08, n)
    silicon_content = np.clip(silicon_base + silicon_noise, 0.2, 0.9)
    
    # Blast pressure (3-5 bar)
    pressure_base = 4.0
    pressure_noise = np.random.normal(0, 0.3, n)
    blast_pressure = np.clip(pressure_base + pressure_noise, 3.0, 5.0)
    
    # Coke rate (300-500 kg/ton HM)
    coke_base = 400
    coke_noise = np.random.normal(0, 25, n)
    coke_rate = np.clip(coke_base + coke_noise, 320, 480)
    
    # Top gas temperature (150-250°C)
    top_gas_base = 200
    top_gas_noise = np.random.normal(0, 20, n)
    top_gas_temp = np.clip(top_gas_base + top_gas_noise, 140, 260)
    
    # Oxygen enrichment (2-5%)
    oxygen_base = 3.5
    oxygen_noise = np.random.normal(0, 0.5, n)
    oxygen_enrichment = np.clip(oxygen_base + oxygen_noise, 2.0, 5.0)
    
    # Create DataFrame
    df = pd.DataFrame({
        'timestamp': timestamps,
        'hot_metal_temperature': hot_metal_temp,
        'silicon_content': silicon_content,
        'blast_pressure': blast_pressure,
        'coke_rate': coke_rate,
        'top_gas_temperature': top_gas_temp,
        'oxygen_enrichment': oxygen_enrichment
    })
    
    df.set_index('timestamp', inplace=True)
    
    # Add some anomalies for testing
    anomaly_indices = np.random.choice(n, size=5, replace=False)
    df.loc[df.index[anomaly_indices], 'hot_metal_temperature'] += 50
    df.loc[df.index[anomaly_indices], 'silicon_content'] += 0.2
    
    return df


# Request/Response Models
class AnalyticsRequest(BaseModel):
    target_parameters: List[str] = Field(..., description="Parameters to analyze")
    candidate_factors: Optional[List[str]] = Field(None, description="Factors for root cause analysis")
    time_range_hours: int = Field(default=168, description="Hours of historical data")


class ChatRequest(BaseModel):
    query: str = Field(..., description="User's query")
    session_id: str = Field(default="default_session", description="Conversation session ID")


class ChatResponse(BaseModel):
    response: str
    intent: str
    confidence: float
    entities: Dict[str, Any]
    session_id: str
    timestamp: str


@router.get("/mock-data")
async def get_mock_data(hours: int = Query(default=168, ge=1, le=720)):
    """Get mock furnace data for testing"""
    df = generate_mock_furnace_data(hours)
    
    return {
        "records": len(df),
        "parameters": list(df.columns),
        "time_range": {
            "start": str(df.index.min()),
            "end": str(df.index.max())
        },
        "sample_data": df.head(10).to_dict()
    }


@router.post("/spc-analysis")
async def perform_spc_analysis(request: AnalyticsRequest):
    """
    Perform Statistical Process Control analysis on specified parameters
    """
    try:
        # Generate mock data
        df = generate_mock_furnace_data(request.time_range_hours)
        
        # Use provided factors or default to all other columns
        candidate_factors = request.candidate_factors or [
            col for col in df.columns if col not in request.target_parameters
        ]
        
        # Run analytics
        engine = AdvancedAnalyticsEngine()
        report = engine.generate_analytics_report(
            df=df,
            target_parameters=request.target_parameters,
            candidate_factors=candidate_factors
        )
        
        return {
            "success": True,
            "analysis": report
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/correlation-analysis")
async def perform_correlation_analysis(
    hours: int = Query(default=168, ge=24, le=720),
    method: str = Query(default="pearson", regex="^(pearson|spearman|kendall)$")
):
    """
    Perform correlation analysis on all parameters
    """
    try:
        df = generate_mock_furnace_data(hours)
        numeric_df = df.select_dtypes(include=[np.number])
        
        engine = AdvancedAnalyticsEngine()
        result = engine.analyze_correlations(numeric_df, method=method)
        
        return {
            "success": True,
            "correlation_matrix": result.correlation_matrix.to_dict(),
            "significant_correlations": result.significant_correlations,
            "method": method,
            "data_points": len(df)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/root-cause-analysis")
async def perform_root_cause_analysis(
    target_parameter: str = Query(..., description="Parameter showing anomaly"),
    hours: int = Query(default=168, ge=24, le=720)
):
    """
    Perform root cause analysis for a specific parameter
    """
    try:
        df = generate_mock_furnace_data(hours)
        
        if target_parameter not in df.columns:
            raise HTTPException(
                status_code=400,
                detail=f"Parameter '{target_parameter}' not found. Available: {list(df.columns)}"
            )
        
        candidate_factors = [col for col in df.columns if col != target_parameter]
        
        engine = AdvancedAnalyticsEngine()
        findings = engine.perform_root_cause_analysis(
            target_parameter=target_parameter,
            candidate_factors=candidate_factors,
            df=df
        )
        
        return {
            "success": True,
            "target_parameter": target_parameter,
            "findings": [
                {
                    "factor": f.factor,
                    "contribution_percentage": f.contribution_percentage,
                    "correlation_strength": f.correlation_strength,
                    "temporal_lag_hours": f.temporal_lag_hours,
                    "confidence_score": f.confidence_score,
                    "evidence": f.evidence,
                    "recommendation": f.recommendation
                }
                for f in findings
            ],
            "data_points": len(df)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quick-analytics")
async def get_quick_analytics(hours: int = Query(default=168, ge=24, le=720)):
    """
    Get quick analytics summary for all parameters
    """
    try:
        df = generate_mock_furnace_data(hours)
        target_params = ['hot_metal_temperature', 'silicon_content', 'coke_rate']
        
        report = quick_analytics(df, target_params)
        
        return {
            "success": True,
            "report": report
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Chatbot routes
chat_router = APIRouter(prefix="/chatbot", tags=["AI Chatbot"])

# Global chatbot instance (in production, use dependency injection with proper lifecycle)
_chatbot_instances: Dict[str, ChatbotAssistant] = {}


def get_chatbot() -> ChatbotAssistant:
    """Get or create chatbot instance"""
    api_key = "demo_key"  # In production, get from environment
    
    if "default" not in _chatbot_instances:
        try:
            _chatbot_instances["default"] = ChatbotAssistant(api_key=api_key)
        except ValueError:
            # If no API key, return mock responses
            pass
    
    return _chatbot_instances.get("default")


@chat_router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(request: ChatRequest):
    """
    Chat with the AI assistant for blast furnace analytics
    """
    try:
        # Check if we have a real chatbot
        chatbot = get_chatbot()
        
        if not chatbot:
            # Return mock response for demo without API key
            return ChatResponse(
                response="I'm currently in demo mode. To enable full AI capabilities, please set the GEMINI_API_KEY environment variable. Your query was: " + request.query,
                intent="general_question",
                confidence=0.5,
                entities={"query": request.query},
                session_id=request.session_id,
                timestamp=datetime.now().isoformat()
            )
        
        # Generate mock data context
        df = generate_mock_furnace_data(168)
        data_context = {
            "available_parameters": list(df.columns),
            "latest_values": df.iloc[-1].to_dict(),
            "time_range": str(df.index.min()) + " to " + str(df.index.max())
        }
        
        # Get response from chatbot
        result = chatbot.chat(
            query=request.query,
            session_id=request.session_id,
            data_context=data_context
        )
        
        return ChatResponse(
            response=result["response"],
            intent=result["intent"],
            confidence=result["confidence"],
            entities=result["entities"],
            session_id=result["session_id"],
            timestamp=result["timestamp"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@chat_router.get("/conversation/{session_id}")
async def get_conversation_summary(session_id: str):
    """Get conversation history and summary"""
    try:
        chatbot = get_chatbot()
        
        if not chatbot:
            return {"message": "Chatbot not initialized", "session_id": session_id}
        
        summary = chatbot.get_conversation_summary(session_id)
        
        if not summary:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return summary
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@chat_router.delete("/conversation/{session_id}")
async def clear_conversation(session_id: str):
    """Clear conversation history"""
    try:
        chatbot = get_chatbot()
        
        if not chatbot:
            return {"message": "Chatbot not initialized"}
        
        success = chatbot.clear_conversation(session_id)
        
        return {
            "success": success,
            "message": "Conversation cleared" if success else "Session not found"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@chat_router.get("/intents")
async def list_supported_intents():
    """List all supported intent types"""
    return {
        "intents": [
            {
                "type": intent.value,
                "description": get_intent_description(intent.value)
            }
            for intent in IntentType
        ]
    }


def get_intent_description(intent_type: str) -> str:
    """Get description for intent type"""
    descriptions = {
        "data_query": "Retrieve historical data for specific parameters",
        "analytics_request": "Request statistical analysis (SPC, correlation, etc.)",
        "anomaly_investigation": "Investigate causes of anomalies or deviations",
        "forecast_request": "Predict future values for parameters",
        "explanation_request": "Explain concepts, metrics, or methodologies",
        "comparison_request": "Compare different time periods or parameters",
        "trend_analysis": "Analyze trends and patterns in data",
        "root_cause_inquiry": "Identify root causes of issues",
        "general_question": "General questions about operations",
        "greeting": "Greetings and salutations",
        "farewell": "Goodbye and conversation ending",
        "unknown": "Unrecognized intent"
    }
    return descriptions.get(intent_type, "No description available")


# Include routers in main app
def include_routers(app):
    """Include all analytics routers in the FastAPI app"""
    app.include_router(router)
    app.include_router(chat_router)

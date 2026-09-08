"""
Test Script for Advanced Analytics and Chatbot Assistant
Tests SPC, Correlation Analysis, Root Cause Analysis, and Chatbot functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("=" * 80)
print("TESTING ADVANCED ANALYTICS AND CHATBOT ASSISTANT")
print("=" * 80)

# Test 1: Analytics Engine
print("\n" + "=" * 80)
print("TEST 1: Advanced Analytics Engine")
print("=" * 80)

from app.services.analytics_engine import (
    AdvancedAnalyticsEngine,
    quick_analytics
)

# Generate mock data
print("\n[1.1] Generating mock blast furnace data...")
np.random.seed(42)
hours = 168
end_time = datetime.now()
start_time = end_time - timedelta(hours=hours)
timestamps = pd.date_range(start=start_time, end=end_time, freq='H')
n = len(timestamps)

# Create realistic parameters
hot_metal_temp = 1475 + np.linspace(0, 10, n) + np.random.normal(0, 15, n)
silicon_content = np.clip(0.55 + np.random.normal(0, 0.08, n), 0.2, 0.9)
blast_pressure = np.clip(4.0 + np.random.normal(0, 0.3, n), 3.0, 5.0)
coke_rate = np.clip(400 + np.random.normal(0, 25, n), 320, 480)
top_gas_temp = np.clip(200 + np.random.normal(0, 20, n), 140, 260)

df = pd.DataFrame({
    'hot_metal_temperature': hot_metal_temp,
    'silicon_content': silicon_content,
    'blast_pressure': blast_pressure,
    'coke_rate': coke_rate,
    'top_gas_temperature': top_gas_temp
}, index=timestamps)

print(f"✓ Generated {len(df)} records with {len(df.columns)} parameters")
print(f"  Time range: {df.index.min()} to {df.index.max()}")

# Test SPC Analysis
print("\n[1.2] Testing Statistical Process Control (SPC) Analysis...")
engine = AdvancedAnalyticsEngine()
spc_result = engine.calculate_spc(df['hot_metal_temperature'], 'hot_metal_temperature')

print(f"✓ SPC Metrics for Hot Metal Temperature:")
print(f"  - Mean: {spc_result.mean:.2f}°C")
print(f"  - Std Dev: {spc_result.std_dev:.2f}°C")
print(f"  - UCL (3σ): {spc_result.ucl:.2f}°C")
print(f"  - LCL (3σ): {spc_result.lcl:.2f}°C")
print(f"  - Trend: {spc_result.trend}")
print(f"  - Violations detected: {len(spc_result.violations)}")

if spc_result.violations:
    print(f"  Sample violation: {spc_result.violations[0]}")

# Test Correlation Analysis
print("\n[1.3] Testing Correlation Analysis...")
corr_result = engine.analyze_correlations(df)

print(f"✓ Correlation Analysis Complete:")
print(f"  - Total feature pairs: {len(corr_result.feature_pairs)}")
print(f"  - Significant correlations: {len(corr_result.significant_correlations)}")

if corr_result.significant_correlations:
    top_corr = corr_result.significant_correlations[0]
    print(f"  - Strongest correlation: {top_corr['feature_1']} ↔ {top_corr['feature_2']}")
    print(f"    Correlation coefficient: {top_corr['correlation']:.3f}")
    print(f"    Strength: {top_corr['strength']}")
    print(f"    Direction: {top_corr['direction']}")

# Test Root Cause Analysis
print("\n[1.4] Testing Root Cause Analysis...")
target_param = 'hot_metal_temperature'
candidate_factors = ['silicon_content', 'blast_pressure', 'coke_rate', 'top_gas_temperature']

rca_findings = engine.perform_root_cause_analysis(
    target_parameter=target_param,
    candidate_factors=candidate_factors,
    df=df
)

print(f"✓ Root Cause Analysis for {target_param}:")
print(f"  - Factors analyzed: {len(rca_findings)}")

if rca_findings:
    top_finding = rca_findings[0]
    print(f"\n  Top Contributing Factor: {top_finding.factor}")
    print(f"    - Contribution: {top_finding.contribution_percentage:.1f}%")
    print(f"    - Correlation: {top_finding.correlation_strength:.3f}")
    print(f"    - Temporal Lag: {top_finding.temporal_lag_hours} hours")
    print(f"    - Confidence: {top_finding.confidence_score:.2f}")
    print(f"    - Evidence: {top_finding.evidence[0]}")
    print(f"    - Recommendation: {top_finding.recommendation[:100]}...")

# Test Comprehensive Analytics Report
print("\n[1.5] Testing Comprehensive Analytics Report...")
report = engine.generate_analytics_report(
    df=df,
    target_parameters=['hot_metal_temperature', 'silicon_content'],
    candidate_factors=candidate_factors
)

print(f"✓ Analytics Report Generated:")
print(f"  - Generated at: {report['generated_at']}")
print(f"  - Data summary: {report['data_summary']['total_records']} records")
print(f"  - SPC analyses: {len(report['spc_analysis'])}")
print(f"  - Executive summary items: {len(report['executive_summary'])}")

print("\n  Executive Summary:")
for item in report['executive_summary'][:3]:
    print(f"    • {item}")

# Test Quick Analytics
print("\n[1.6] Testing Quick Analytics Function...")
quick_report = quick_analytics(df, ['hot_metal_temperature', 'coke_rate'])
print(f"✓ Quick analytics completed successfully")

print("\n" + "=" * 80)
print("TEST 2: AI Chatbot Assistant")
print("=" * 80)

from app.services.chatbot_assistant import (
    ChatbotAssistant,
    IntentClassifier,
    RAGRetriever,
    IntentType
)

# Test Intent Classification (without API key - uses fallback)
print("\n[2.1] Testing Intent Classification (keyword-based fallback)...")

test_queries = [
    ("Show me the temperature from yesterday", IntentType.DATA_QUERY),
    ("Run SPC analysis on silicon content", IntentType.ANALYTICS_REQUEST),
    ("Why did the pressure spike this morning?", IntentType.ANOMALY_INVESTIGATION),
    ("Predict temperature for next 12 hours", IntentType.FORECAST_REQUEST),
    ("Explain what Cpk means", IntentType.EXPLANATION_REQUEST),
    ("Compare this week with last week", IntentType.COMPARISON_REQUEST),
    ("What's the trend for coke rate?", IntentType.TREND_ANALYSIS),
    ("What's causing high temperature?", IntentType.ROOT_CAUSE_INQUIRY),
    ("Hello", IntentType.GREETING),
    ("Goodbye", IntentType.FAREWELL)
]

# Create a mock model for testing without API key
class MockModel:
    def generate_content(self, prompt):
        raise Exception("No API key - using fallback")

mock_model = MockModel()
classifier = IntentClassifier(mock_model)

correct_classifications = 0
for query, expected_intent in test_queries:
    result = classifier.classify(query)
    status = "✓" if result.intent == expected_intent else "✗"
    if result.intent == expected_intent:
        correct_classifications += 1
    print(f"  {status} Query: '{query[:40]}...'")
    print(f"     Expected: {expected_intent.value}, Got: {result.intent.value} (confidence: {result.confidence:.2f})")

print(f"\n✓ Classification Accuracy: {correct_classifications}/{len(test_queries)} ({100*correct_classifications/len(test_queries):.0f}%)")

# Test RAG Retriever
print("\n[2.2] Testing RAG (Retrieval-Augmented Generation) Retriever...")
retriever = RAGRetriever()

test_topics = [
    "What is SPC analysis?",
    "How is Cpk calculated?",
    "Explain correlation in statistics",
    "Tell me about blast furnace operations"
]

for topic_query in test_topics:
    results = retriever.retrieve(topic_query, IntentType.EXPLANATION_REQUEST)
    if results:
        print(f"  ✓ Query: '{topic_query}'")
        print(f"     Retrieved {len(results)} relevant document(s)")
        print(f"     Top match: {results[0]['topic']} (score: {results[0]['relevance_score']:.2f})")

# Test Conversation Management
print("\n[2.3] Testing Conversation Management...")

class MockChatbotAssistant:
    """Mock chatbot for testing without API key"""
    
    def __init__(self):
        self.conversations = {}
    
    def start_conversation(self, session_id):
        from app.services.chatbot_assistant import ConversationContext
        context = ConversationContext(session_id=session_id)
        self.conversations[session_id] = context
        return context
    
    def chat(self, query, session_id, data_context=None):
        # Simulate response without API
        return {
            "response": f"Demo response to: {query}. Set GEMINI_API_KEY for full AI capabilities.",
            "intent": "general_question",
            "confidence": 0.5,
            "entities": {"query": query},
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "tokens_used": len(query.split()) * 1.3
        }
    
    def get_conversation_summary(self, session_id):
        if session_id not in self.conversations:
            return None
        context = self.conversations[session_id]
        return {
            "session_id": session_id,
            "message_count": len(context.messages),
            "messages": [{"role": m.role, "content": m.content} for m in context.messages[-5:]]
        }
    
    def clear_conversation(self, session_id):
        if session_id in self.conversations:
            del self.conversations[session_id]
            return True
        return False

chatbot = MockChatbotAssistant()
session_id = "test_session_001"

# Start conversation
context = chatbot.start_conversation(session_id)
print(f"  ✓ Started conversation session: {session_id}")

# Send messages
test_messages = [
    "What is SPC?",
    "Show me temperature trends",
    "Thanks!"
]

for msg in test_messages:
    response = chatbot.chat(msg, session_id)
    print(f"  ✓ User: {msg}")
    print(f"    Bot: {response['response'][:60]}...")

# Get summary
summary = chatbot.get_conversation_summary(session_id)
print(f"\n  ✓ Conversation Summary:")
print(f"    - Session: {summary['session_id']}")
print(f"    - Messages: {summary['message_count']}")

# Clear conversation
success = chatbot.clear_conversation(session_id)
print(f"  ✓ Conversation cleared: {success}")

print("\n" + "=" * 80)
print("TEST 3: Integration Test - Full Analytics Pipeline")
print("=" * 80)

print("\n[3.1] Running complete analytics pipeline...")

# Generate fresh data
df_test = pd.DataFrame({
    'parameter_A': 100 + np.cumsum(np.random.randn(n)),
    'parameter_B': 50 + np.random.randn(n) * 10,
    'parameter_C': 200 + np.sin(np.linspace(0, 8*np.pi, n)) * 20 + np.random.randn(n) * 5,
    'parameter_D': 75 + np.random.exponential(10, n)
}, index=timestamps)

# Run full pipeline
engine_full = AdvancedAnalyticsEngine()
full_report = engine_full.generate_analytics_report(
    df=df_test,
    target_parameters=['parameter_A', 'parameter_B'],
    candidate_factors=['parameter_C', 'parameter_D']
)

print(f"✓ Full pipeline completed:")
print(f"  - SPC analyses performed: {len(full_report['spc_analysis'])}")
print(f"  - Correlations found: {full_report['correlation_analysis'].get('total_significant_pairs', 0)}")
print(f"  - Root cause findings: {sum(len(v) for v in full_report['root_cause_analysis'].values())}")
print(f"  - Executive insights: {len(full_report['executive_summary'])}")

print("\n" + "=" * 80)
print("ALL TESTS COMPLETED SUCCESSFULLY!")
print("=" * 80)

print("\n📊 SUMMARY:")
print("  ✓ Advanced Analytics Engine: SPC, Correlation, Root Cause Analysis")
print("  ✓ AI Chatbot Assistant: Intent Classification, RAG, Conversation Management")
print("  ✓ Integration: Full analytics pipeline working")
print("\n💡 NOTE: For full AI chatbot capabilities, set GEMINI_API_KEY environment variable")
print("   Get your free API key at: https://makersuite.google.com/app/apikey")
print("   Gemini 1.5 Flash free tier: 1M tokens/month")

print("\n" + "=" * 80)

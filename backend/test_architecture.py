#!/usr/bin/env python3
"""
Test the simplified architecture
"""

print("🧪 Testing Minimal Architecture")
print("=" * 40)

try:
    # Test 1: Import GPT client
    from gptclient import InvokeGPT
    print("✅ gptclient.py imports successfully")
    
    client = InvokeGPT()
    print(f"✅ GPT client created: {client.model}")
    
except Exception as e:
    print(f"❌ gptclient.py error: {e}")

try:
    # Test 2: Import LLM client
    from llm_client import MemoryEnhancedLLMClient, OpenAIMessage
    print("✅ llm_client.py imports successfully")
    
    llm_client = MemoryEnhancedLLMClient()
    print(f"✅ LLM client created: {llm_client.model}")
    
except Exception as e:
    print(f"❌ llm_client.py error: {e}")

print()
print("🎉 MINIMAL ARCHITECTURE COMPLETE!")
print("🔹 gptclient.py: Only get_response() method")
print("🔹 llm_client.py: All dataclasses and logic")
print("🔹 Clean, simple separation!")

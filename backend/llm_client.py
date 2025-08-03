"""
Custom LLM Client with Memory System and Data Analysis
Provides AI chat functionality with semantic memory and data analysis capabilities
"""

import asyncio
import random
import re
import json
import logging
from typing import List, Dict, Any, Optional
from gptclient import InvokeGPT, OpenAIMessage, ChatCompletionResponse, create_openai_message
from memory_system import memory_system
from data_tools import data_analyzer


class MemoryEnhancedLLMClient:
    """
    Enhanced LLM Client with memory system and data analysis capabilities
    Uses InvokeGPT for core OpenAI functionality and adds memory/data features
    """
    
    def __init__(self, model: str = "gpt-4o-mini"):
        self.gpt_client = InvokeGPT(model=model)
        self.model = model
    
    async def get_response(self, messages: List[OpenAIMessage]) -> ChatCompletionResponse:
        """
        Get response from LLM with memory-enhanced context and data analysis
        
        Args:
            messages: List of conversation messages
            
        Returns:
            ChatCompletionResponse with generated content
        """
        try:
            # Get the latest user message for memory context
            user_message = next((msg.content for msg in reversed(messages) if msg.role == "user"), "")
            
            # Check if this is a data analysis request
            is_data_request = self._is_data_analysis_request(user_message)
            
            # Handle data analysis directly if needed
            if is_data_request and data_analyzer.data is not None:
                response_content = self._handle_data_analysis(user_message)
                if response_content:
                    # Store conversation in memory
                    memory_system.add_conversation_turn(
                        user_message=user_message,
                        assistant_message=response_content,
                        metadata={"has_data": True, "model": self.model, "type": "data_analysis"}
                    )
                    
                    return ChatCompletionResponse(
                        choices=[{
                            "message": {
                                "role": "assistant",
                                "content": response_content
                            }
                        }],
                        usage={
                            "prompt_tokens": len(user_message) // 4,
                            "completion_tokens": len(response_content) // 4,
                            "total_tokens": (len(user_message) + len(response_content)) // 4
                        }
                    )
            
            # Get relevant context from memory
            memory_context = memory_system.get_conversation_context(user_message)
            
            # Handle memory-specific queries
            memory_response = self._handle_memory_queries(user_message)
            if memory_response:
                # Store conversation in memory
                memory_system.add_conversation_turn(
                    user_message=user_message,
                    assistant_message=memory_response,
                    metadata={"has_data": data_analyzer.data is not None, "model": self.model, "type": "memory_query"}
                )
                
                return ChatCompletionResponse(
                    choices=[{
                        "message": {
                            "role": "assistant",
                            "content": memory_response
                        }
                    }],
                    usage={
                        "prompt_tokens": len(user_message) // 4,
                        "completion_tokens": len(memory_response) // 4,
                        "total_tokens": (len(user_message) + len(memory_response)) // 4
                    }
                )
            
            # Build enhanced system message with memory context
            system_content = "You are a helpful AI assistant with access to conversation history and uploaded data. Provide clear, concise, and helpful responses."
            
            if memory_context:
                system_content += f"\n\nRelevant context from previous conversations and data:\n{memory_context}"
            
            if data_analyzer.data is not None:
                system_content += "\n\nYou have access to uploaded data and can perform data analysis and create visualizations."
            
            # Get response from GPT client with enhanced system message
            response = await self.gpt_client.get_response(messages, system_content)
            
            # Extract assistant message
            assistant_message = response.choices[0]["message"]["content"]
            
            # Store conversation in memory
            if user_message:
                memory_system.add_conversation_turn(
                    user_message=user_message,
                    assistant_message=assistant_message,
                    metadata={"has_data": data_analyzer.data is not None, "model": self.model, "type": "chat"}
                )
                
                # Save memory periodically
                if len(memory_system.memories) % 10 == 0:
                    memory_system.save_memories()
            
            return response
            
        except Exception as e:
            logging.error(f"Error getting LLM response: {e}")
            return self._create_fallback_response(f"I encountered an error: {str(e)}")
    
    def _is_data_analysis_request(self, user_message: str) -> bool:
        """Check if the user message is requesting data analysis"""
        message_lower = user_message.lower()
        
        data_keywords = [
            'how many', 'count', 'rows', 'columns', 'summary', 'describe', 
            'missing', 'null', 'unique', 'show data', 'data types',
            'histogram', 'distribution', 'scatter', 'correlation', 'relationship',
            'bar chart', 'bar graph', 'count by', 'line chart', 'line graph', 
            'trend', 'correlation matrix', 'heatmap', 'box plot', 'box chart',
            'suggest chart', 'what chart', 'visualize', 'plot'
        ]
        
        return any(keyword in message_lower for keyword in data_keywords)
    
    def _handle_memory_queries(self, user_message: str) -> Optional[str]:
        """Handle memory-specific queries"""
        message_lower = user_message.lower()
        
        # Check for memory-related queries
        if any(phrase in message_lower for phrase in ['what did we discuss', 'what data', 'previous files', 'memory', 'remember', 'recall']):
            stats = memory_system.get_memory_stats()
            recent_memories = memory_system.get_recent_memories(hours=24)
            
            response = f"I have {stats['total_memories']} memories stored. "
            if recent_memories:
                response += f"In the last 24 hours, we've discussed:\n"
                for memory in recent_memories[:3]:
                    content_preview = memory.content[:100].replace('\n', ' ')
                    response += f"- {content_preview}...\n"
            else:
                response += "No recent conversations found."
            
            # Add memory type breakdown
            if 'entry_types' in stats:
                response += f"\nMemory breakdown: {dict(stats['entry_types'])}"
            
            return response
        
        # Handle "remember when" or "previous" queries
        if any(word in message_lower for word in ['remember when', 'previous', 'before', 'earlier', 'told', 'said']):
            # Search for relevant memories
            relevant_memories = memory_system.search_memories(user_message, k=3, min_similarity=0.3)
            if relevant_memories:
                response = "I found some relevant previous conversations:\n\n"
                for i, (memory, similarity) in enumerate(relevant_memories, 1):
                    content_preview = memory.content[:200].replace('\n', ' ')
                    response += f"{i}. {content_preview}...\n"
                response += "\nIs this what you were referring to?"
                return response
        
        return None
    
    def _handle_data_analysis(self, user_message: str) -> Optional[str]:
        """Handle data analysis queries with memory integration"""
        message_lower = user_message.lower()
        
        # Data querying
        if any(phrase in message_lower for phrase in [
            'how many', 'count', 'rows', 'columns', 'summary', 'describe', 
            'missing', 'null', 'unique', 'show data', 'data types'
        ]):
            result = data_analyzer.query_data(user_message)
            if "error" in result:
                return f"Error: {result['error']}"
            
            response = "\n".join(result.get("results", ["No results found."]))
            
            # Store analysis result in memory
            memory_system.add_analysis_result(
                query=user_message,
                result=response,
                metadata={"query_type": "data_info"}
            )
            
            return response
        
        # Chart creation requests
        chart_type = None
        if any(word in message_lower for word in ['histogram', 'distribution']):
            chart_type = "histogram"
        elif any(word in message_lower for word in ['scatter', 'correlation', 'relationship']):
            chart_type = "scatter"
        elif any(word in message_lower for word in ['bar chart', 'bar graph', 'count by']):
            chart_type = "bar"
        elif any(word in message_lower for word in ['line chart', 'line graph', 'trend']):
            chart_type = "line"
        elif any(word in message_lower for word in ['correlation matrix', 'heatmap']):
            chart_type = "correlation"
        elif any(word in message_lower for word in ['box plot', 'box chart']):
            chart_type = "box"
        
        if chart_type:
            # Extract column names from message if mentioned
            columns = self._extract_column_names(user_message)
            chart_params = {}
            
            if chart_type in ["scatter", "line"] and len(columns) >= 2:
                chart_params = {"x_col": columns[0], "y_col": columns[1]}
            elif chart_type in ["histogram", "box"] and len(columns) >= 1:
                chart_params = {"column": columns[0]}
            elif chart_type == "bar" and len(columns) >= 1:
                chart_params = {"x_col": columns[0]}
            
            result = data_analyzer.create_visualization(chart_type, **chart_params)
            if "error" in result:
                return f"Error creating chart: {result['error']}"
            
            response = f"📊 Created {result['chart_type']} chart: {result['title']}\n{result['description']}\n\n[CHART:{result['chart_id']}:{result['plotly_json']}]"
            
            # Store chart info in memory
            memory_system.add_chart_info(chart_type, result)
            
            return response
        
        # Chart suggestions
        if any(phrase in message_lower for phrase in ['suggest chart', 'what chart', 'visualize', 'plot']):
            suggestions = data_analyzer.get_chart_suggestions()
            if not suggestions:
                return "No chart suggestions available. Please upload data first."
            
            response = "Here are some chart suggestions based on your data:\n\n"
            for i, suggestion in enumerate(suggestions[:3], 1):
                response += f"{i}. **{suggestion['title']}** - {suggestion['description']}\n"
            response += "\nJust ask me to create any of these charts!"
            
            # Store suggestion request in memory
            memory_system.add_analysis_result(
                query=user_message,
                result=response,
                metadata={"query_type": "chart_suggestions"}
            )
            
            return response
        
        return None
    
    def _extract_column_names(self, message: str) -> List[str]:
        """Extract potential column names from user message"""
        if data_analyzer.data is None:
            return []
        
        columns = list(data_analyzer.data.columns)
        found_columns = []
        
        message_lower = message.lower()
        for col in columns:
            if col.lower() in message_lower:
                found_columns.append(col)
        
        return found_columns
    
    def _create_fallback_response(self, error_message: str) -> ChatCompletionResponse:
        """Create a fallback response for errors"""
        return ChatCompletionResponse(
            choices=[{
                "message": {
                    "role": "assistant",
                    "content": error_message
                }
            }],
            usage={
                "prompt_tokens": 0,
                "completion_tokens": len(error_message) // 4,
                "total_tokens": len(error_message) // 4
            }
        )


# Type aliases for compatibility
OpenAIResponse = ChatCompletionResponse

def format_messages_for_llm(messages: List[Dict[str, str]]) -> List[OpenAIMessage]:
    """Convert message dictionaries to OpenAIMessage objects"""
    return [
        OpenAIMessage(role=msg['role'], content=msg['content'])
        for msg in messages
    ]


# Example usage and testing
async def main():
    """Test the memory-enhanced LLM client"""
    client = MemoryEnhancedLLMClient()
    
    # Test messages
    test_messages = [
        OpenAIMessage(role="user", content="Hello, can you help me with data analysis?"),
    ]
    
    print("Testing memory-enhanced LLM client...")
    print(f"Using model: {client.model}")
    print(f"Memory system active: {len(memory_system.memories)} memories stored")
    
    response = await client.get_response(test_messages)
    
    print(f"Response: {response.choices[0]['message']['content']}")
    print(f"Token usage: {response.usage}")


if __name__ == "__main__":
    asyncio.run(main())

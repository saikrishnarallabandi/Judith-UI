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
from dataclasses import dataclass
from gptclient import InvokeGPT
from memory_client import MemoryClient
from data_tools import data_analyzer


@dataclass
class OpenAIMessage:
    """Represents a message in OpenAI format"""
    role: str  # 'system', 'user', or 'assistant'
    content: str





def create_openai_message(role: str, content: str) -> OpenAIMessage:
    """Create a new OpenAI format message"""
    return OpenAIMessage(role=role, content=content)


class MemoryEnhancedLLMClient:
    """
    Enhanced LLM Client with memory system and data analysis capabilities
    Uses InvokeGPT for core OpenAI functionality and adds memory/data features
    """
    
    def __init__(self, model: str = "gpt-4o-mini"):
        self.gpt_client = InvokeGPT(model=model)
        self.memory_client = MemoryClient()
        self.model = model
    
    async def get_response(self, messages: List[OpenAIMessage]) -> str:
        """
        Get response from LLM with memory-enhanced context and data analysis
        
        Args:
            messages: List of conversation messages
            
        Returns:
            Assistant response content as string
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
                    self.memory_client.store_conversation(
                        user_message=user_message,
                        assistant_message=response_content,
                        metadata={"has_data": True, "model": self.model, "type": "data_analysis"}
                    )
                    
                    return response_content
            
            # Handle memory-specific queries
            memory_response = self.memory_client.handle_memory_query(user_message)
            if memory_response:
                # Store conversation in memory
                self.memory_client.store_conversation(
                    user_message=user_message,
                    assistant_message=memory_response,
                    metadata={"has_data": data_analyzer.data is not None, "model": self.model, "type": "memory_query"}
                )
                
                return memory_response
            
            # Build enhanced messages with memory context and system message
            enhanced_messages = self._build_enhanced_messages(messages, user_message)
            
            # Convert to OpenAI format
            openai_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in enhanced_messages
            ]
            
            # Get response from GPT client (wrap sync call in async)
            response = await asyncio.get_event_loop().run_in_executor(
                None, self.gpt_client.get_response, openai_messages
            )
            
            # Extract assistant message from OpenAI response
            assistant_message = response.choices[0].message.content or "I apologize, but I couldn't generate a response."
            
            # Store conversation in memory
            if user_message:
                self.memory_client.store_conversation(
                    user_message=user_message,
                    assistant_message=assistant_message,
                    metadata={"has_data": data_analyzer.data is not None, "model": self.model, "type": "chat"}
                )
                
                # Save memory periodically
                if self.memory_client.should_save_memories():
                    self.memory_client.save_memories()
            
            return assistant_message
            
        except Exception as e:
            logging.error(f"Error getting LLM response: {e}")
            return f"I encountered an error: {str(e)}"
    
    def _build_enhanced_messages(self, messages: List[OpenAIMessage], user_message: str) -> List[OpenAIMessage]:
        """
        Build enhanced message list with system message including memory context
        
        Args:
            messages: Original conversation messages
            user_message: Latest user message for memory context
            
        Returns:
            Enhanced message list with system message
        """
        # Get relevant context from memory
        memory_context = self.memory_client.get_conversation_context(user_message)
        
        # Build enhanced system message
        system_content = "You are a helpful AI assistant with access to conversation history and uploaded data. Provide clear, concise, and helpful responses."
        
        if memory_context:
            system_content += f"\n\nRelevant context from previous conversations and data:\n{memory_context}"
        
        if data_analyzer.data is not None:
            system_content += "\n\nYou have access to uploaded data and can perform data analysis and create visualizations."
        
        # Create enhanced message list
        enhanced_messages = []
        
        # Add system message
        enhanced_messages.append(OpenAIMessage(role="system", content=system_content))
        
        # Add conversation messages (skip existing system messages)
        for msg in messages:
            if msg.role != "system":
                enhanced_messages.append(msg)
        
        return enhanced_messages
    
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
            self.memory_client.store_analysis_result(
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
            self.memory_client.store_chart_info(chart_type, result)
            
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
            self.memory_client.store_analysis_result(
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
    print(f"Memory system active: {client.memory_client.get_memory_count()} memories stored")
    
    response = await client.get_response(test_messages)
    
    print(f"Response: {response.choices[0]['message']['content']}")
    print(f"Token usage: {response.usage}")


if __name__ == "__main__":
    asyncio.run(main())

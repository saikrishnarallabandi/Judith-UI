"""
Memory Client for LLM Integration
Handles memory-specific queries and operations
"""

from typing import Optional, List
from memory_system import memory_system
from data_tools import data_analyzer


class MemoryClient:
    """
    Memory client for handling memory-related operations
    """
    
    def __init__(self):
        pass
    
    def is_memory_query(self, user_message: str) -> bool:
        """Check if the user message is requesting memory information"""
        message_lower = user_message.lower()
        
        memory_keywords = [
            'what did we discuss', 'what data', 'previous files', 'memory', 
            'remember', 'recall', 'remember when', 'previous', 'before', 
            'earlier', 'told', 'said', 'history', 'past', 'yesterday'
        ]
        
        return any(keyword in message_lower for keyword in memory_keywords)
    
    def handle_memory_query(self, user_message: str) -> Optional[str]:
        """Handle memory-specific queries"""
        message_lower = user_message.lower()
        
        # Check for general memory-related queries
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
    
    def get_conversation_context(self, user_message: str) -> str:
        """Get relevant context from memory for the conversation"""
        return memory_system.get_conversation_context(user_message)
    
    def store_conversation(self, user_message: str, assistant_message: str, metadata: dict):
        """Store a conversation turn in memory"""
        memory_system.add_conversation_turn(
            user_message=user_message,
            assistant_message=assistant_message,
            metadata=metadata
        )
    
    def store_analysis_result(self, query: str, result: str, metadata: dict):
        """Store data analysis result in memory"""
        memory_system.add_analysis_result(
            query=query,
            result=result,
            metadata=metadata
        )
    
    def store_chart_info(self, chart_type: str, result: dict):
        """Store chart creation info in memory"""
        memory_system.add_chart_info(chart_type, result)
    
    def save_memories(self):
        """Save memories to disk"""
        memory_system.save_memories()
    
    def get_memory_count(self) -> int:
        """Get total number of stored memories"""
        return len(memory_system.memories)
    
    def should_save_memories(self) -> bool:
        """Check if memories should be saved (every 10 conversations)"""
        return len(memory_system.memories) % 10 == 0
    
    def add_file_data(self, filename: str, result: dict):
        """Add file upload data to memory"""
        memory_system.add_file_data(filename, result)
    
    def get_memory_stats(self) -> dict:
        """Get memory statistics"""
        return memory_system.get_memory_stats()
    
    def search_memories(self, query: str, k: int = 5, min_similarity: float = 0.3):
        """Search memories for relevant content"""
        return memory_system.search_memories(query, k, min_similarity)

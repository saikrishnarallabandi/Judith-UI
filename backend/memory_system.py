"""
Memory System for Chat Interface
Provides semantic memory with FAISS-based retrieval for context awareness
"""

import os
import json
import pickle
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import faiss
from sentence_transformers import SentenceTransformer
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MemoryEntry:
    """Represents a single memory entry"""
    
    def __init__(self, content: str, entry_type: str, metadata: Dict[str, Any] = None, timestamp: datetime = None):
        self.content = content
        self.entry_type = entry_type  # 'conversation', 'file_data', 'analysis', 'chart'
        self.metadata = metadata or {}
        self.timestamp = timestamp or datetime.now()
        self.embedding = None
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            'content': self.content,
            'entry_type': self.entry_type,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat(),
            'embedding': self.embedding.tolist() if self.embedding is not None else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryEntry':
        entry = cls(
            content=data['content'],
            entry_type=data['entry_type'],
            metadata=data['metadata'],
            timestamp=datetime.fromisoformat(data['timestamp'])
        )
        if data.get('embedding'):
            entry.embedding = np.array(data['embedding'])
        return entry


class SemanticMemory:
    """Semantic memory system using FAISS for efficient similarity search"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", memory_dir: str = "memory_store"):
        self.model_name = model_name
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)
        
        # Initialize sentence transformer
        try:
            self.encoder = SentenceTransformer(model_name)
            self.embedding_dim = self.encoder.get_sentence_embedding_dimension()
        except Exception as e:
            logger.error(f"Failed to load sentence transformer: {e}")
            raise
        
        # Initialize FAISS index
        self.index = faiss.IndexFlatIP(self.embedding_dim)  # Inner product for cosine similarity
        self.memories: List[MemoryEntry] = []
        
        # Load existing memories
        self.load_memories()
    
    def add_memory(self, content: str, entry_type: str, metadata: Dict[str, Any] = None) -> None:
        """Add a new memory entry"""
        try:
            # Create memory entry
            memory = MemoryEntry(content, entry_type, metadata)
            
            # Generate embedding
            memory.embedding = self.encoder.encode([content])[0]
            
            # Normalize for cosine similarity
            memory.embedding = memory.embedding / np.linalg.norm(memory.embedding)
            
            # Add to FAISS index
            self.index.add(memory.embedding.reshape(1, -1))
            
            # Add to memory list
            self.memories.append(memory)
            
            logger.info(f"Added memory: {entry_type} - {content[:50]}...")
            
        except Exception as e:
            logger.error(f"Failed to add memory: {e}")
    
    def search_memories(self, query: str, k: int = 5, min_similarity: float = 0.3) -> List[Tuple[MemoryEntry, float]]:
        """Search for relevant memories using semantic similarity"""
        try:
            if len(self.memories) == 0:
                return []
            
            # Encode query
            query_embedding = self.encoder.encode([query])[0]
            query_embedding = query_embedding / np.linalg.norm(query_embedding)
            
            # Search FAISS index
            similarities, indices = self.index.search(query_embedding.reshape(1, -1), min(k, len(self.memories)))
            
            # Filter by minimum similarity and return results
            results = []
            for similarity, idx in zip(similarities[0], indices[0]):
                if similarity >= min_similarity and idx < len(self.memories):
                    results.append((self.memories[idx], float(similarity)))
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search memories: {e}")
            return []
    
    def get_recent_memories(self, hours: int = 24, entry_types: List[str] = None) -> List[MemoryEntry]:
        """Get recent memories within specified time window"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_memories = [
            memory for memory in self.memories
            if memory.timestamp >= cutoff_time
        ]
        
        if entry_types:
            recent_memories = [
                memory for memory in recent_memories
                if memory.entry_type in entry_types
            ]
        
        return sorted(recent_memories, key=lambda m: m.timestamp, reverse=True)
    
    def get_conversation_context(self, query: str, max_context_length: int = 2000) -> str:
        """Get relevant context for a query from memory"""
        try:
            # Search for relevant memories
            relevant_memories = self.search_memories(query, k=10, min_similarity=0.2)
            
            # Also get recent conversation memories
            recent_memories = self.get_recent_memories(hours=2, entry_types=['conversation', 'file_data'])
            
            # Combine and deduplicate
            all_memories = relevant_memories + [(m, 0.0) for m in recent_memories]
            seen_content = set()
            unique_memories = []
            
            for memory, similarity in all_memories:
                if memory.content not in seen_content:
                    unique_memories.append((memory, similarity))
                    seen_content.add(memory.content)
            
            # Sort by relevance and recency
            unique_memories.sort(key=lambda x: (x[1], x[0].timestamp), reverse=True)
            
            # Build context string
            context_parts = []
            current_length = 0
            
            for memory, similarity in unique_memories:
                entry_text = f"[{memory.entry_type.upper()}] {memory.content}"
                if current_length + len(entry_text) > max_context_length:
                    break
                
                context_parts.append(entry_text)
                current_length += len(entry_text)
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Failed to get conversation context: {e}")
            return ""
    
    def add_conversation_turn(self, user_message: str, assistant_message: str, metadata: Dict[str, Any] = None) -> None:
        """Add a conversation turn to memory"""
        conversation_content = f"User: {user_message}\nAssistant: {assistant_message}"
        self.add_memory(conversation_content, "conversation", metadata)
    
    def add_file_data(self, filename: str, file_info: Dict[str, Any]) -> None:
        """Add file data information to memory"""
        content = f"File: {filename}\n"
        content += f"Shape: {file_info.get('shape', 'Unknown')}\n"
        content += f"Columns: {', '.join(file_info.get('columns', []))}\n"
        
        if 'summary' in file_info:
            summary = file_info['summary']
            if 'basic_info' in summary:
                content += f"Rows: {summary['basic_info'].get('rows', 'Unknown')}, "
                content += f"Columns: {summary['basic_info'].get('columns', 'Unknown')}\n"
            
            if 'column_types' in summary:
                types = summary['column_types']
                if types.get('numeric'):
                    content += f"Numeric columns: {', '.join(types['numeric'])}\n"
                if types.get('categorical'):
                    content += f"Categorical columns: {', '.join(types['categorical'])}\n"
        
        self.add_memory(content, "file_data", {"filename": filename, "file_info": file_info})
    
    def add_analysis_result(self, query: str, result: str, metadata: Dict[str, Any] = None) -> None:
        """Add data analysis result to memory"""
        content = f"Analysis Query: {query}\nResult: {result}"
        self.add_memory(content, "analysis", metadata)
    
    def add_chart_info(self, chart_type: str, chart_data: Dict[str, Any]) -> None:
        """Add chart information to memory"""
        content = f"Chart Type: {chart_type}\n"
        content += f"Title: {chart_data.get('title', 'Unknown')}\n"
        content += f"Description: {chart_data.get('description', 'No description')}"
        
        self.add_memory(content, "chart", {"chart_type": chart_type, "chart_data": chart_data})
    
    def save_memories(self) -> None:
        """Save memories to disk"""
        try:
            # Save memory entries
            memories_file = self.memory_dir / "memories.json"
            with open(memories_file, 'w') as f:
                json.dump([memory.to_dict() for memory in self.memories], f, indent=2)
            
            # Save FAISS index
            index_file = self.memory_dir / "faiss_index.bin"
            faiss.write_index(self.index, str(index_file))
            
            logger.info(f"Saved {len(self.memories)} memories to disk")
            
        except Exception as e:
            logger.error(f"Failed to save memories: {e}")
    
    def load_memories(self) -> None:
        """Load memories from disk"""
        try:
            memories_file = self.memory_dir / "memories.json"
            index_file = self.memory_dir / "faiss_index.bin"
            
            if memories_file.exists():
                with open(memories_file, 'r') as f:
                    memory_data = json.load(f)
                
                self.memories = [MemoryEntry.from_dict(data) for data in memory_data]
                
                # Rebuild FAISS index if it exists
                if index_file.exists() and len(self.memories) > 0:
                    self.index = faiss.read_index(str(index_file))
                else:
                    # Rebuild index from embeddings
                    embeddings = []
                    for memory in self.memories:
                        if memory.embedding is not None:
                            embeddings.append(memory.embedding)
                    
                    if embeddings:
                        embeddings_array = np.vstack(embeddings)
                        self.index.add(embeddings_array)
                
                logger.info(f"Loaded {len(self.memories)} memories from disk")
            
        except Exception as e:
            logger.error(f"Failed to load memories: {e}")
    
    def clear_old_memories(self, days: int = 30) -> None:
        """Clear memories older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Find indices of memories to keep
        keep_indices = []
        new_memories = []
        
        for i, memory in enumerate(self.memories):
            if memory.timestamp >= cutoff_date:
                keep_indices.append(i)
                new_memories.append(memory)
        
        # Rebuild FAISS index with kept memories
        if keep_indices:
            embeddings = [self.memories[i].embedding for i in keep_indices if self.memories[i].embedding is not None]
            if embeddings:
                embeddings_array = np.vstack(embeddings)
                self.index = faiss.IndexFlatIP(self.embedding_dim)
                self.index.add(embeddings_array)
        else:
            self.index = faiss.IndexFlatIP(self.embedding_dim)
        
        removed_count = len(self.memories) - len(new_memories)
        self.memories = new_memories
        
        logger.info(f"Removed {removed_count} old memories")
        
        # Save updated memories
        self.save_memories()
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about stored memories"""
        if not self.memories:
            return {"total_memories": 0}
        
        entry_types = {}
        for memory in self.memories:
            entry_types[memory.entry_type] = entry_types.get(memory.entry_type, 0) + 1
        
        oldest_memory = min(self.memories, key=lambda m: m.timestamp)
        newest_memory = max(self.memories, key=lambda m: m.timestamp)
        
        return {
            "total_memories": len(self.memories),
            "entry_types": entry_types,
            "oldest_memory": oldest_memory.timestamp.isoformat(),
            "newest_memory": newest_memory.timestamp.isoformat(),
            "index_size": self.index.ntotal
        }


# Global memory instance
memory_system = SemanticMemory()

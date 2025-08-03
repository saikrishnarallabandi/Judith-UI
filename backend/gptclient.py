"""
Core OpenAI GPT Client
Provides basic OpenAI API integration without memory or data analysis dependencies
"""

import asyncio
import random
import time
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class OpenAIMessage:
    """Represents a message in OpenAI format"""
    role: str  # 'system', 'user', or 'assistant'
    content: str


@dataclass
class ChatCompletionResponse:
    """Response format matching OpenAI API"""
    choices: List[Dict[str, Any]]
    usage: Optional[Dict[str, int]] = None


class InvokeGPT:
    """
    Core OpenAI GPT-4o-mini Client
    Provides basic OpenAI API integration with fallback capabilities
    """
    
    def __init__(self, api_endpoint: str = "/api/chat", model: str = "gpt-4o-mini"):
        self.api_endpoint = api_endpoint
        self.model = model
        self.max_tokens = int(os.getenv("MAX_TOKENS", "1000"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("Warning: OPENAI_API_KEY not found in environment variables. Using fallback mode.")
            self.client = None
        else:
            self.client = AsyncOpenAI(
                api_key=api_key,
                organization=os.getenv("OPENAI_ORG_ID")  # Optional
            )
        
        # Fallback response templates for when API is unavailable
        self.response_templates = [
            "I understand your question about {}. Let me help you with that.",
            "That's an interesting point about {}. Here's what I think:",
            "Thank you for asking about {}. Based on my knowledge:",
            "I'd be happy to explain {} to you.",
            "Regarding {}, here's my perspective:",
        ]
    
    async def get_response(self, messages: List[OpenAIMessage], system_message: str = None) -> ChatCompletionResponse:
        """
        Generate a response using OpenAI GPT-4o-mini
        
        Args:
            messages: List of OpenAI format messages
            system_message: Optional system message to prepend
            
        Returns:
            ChatCompletionResponse with generated content
        """
        # If OpenAI client is available, use the actual API
        if self.client:
            try:
                # Convert our OpenAIMessage objects to the format expected by OpenAI
                openai_messages = [
                    {"role": msg.role, "content": msg.content}
                    for msg in messages
                ]
                
                # Add or update system message
                default_system = "You are a helpful AI assistant. Provide clear, concise, and helpful responses to user questions."
                system_content = system_message or default_system
                
                if not openai_messages or openai_messages[0]["role"] != "system":
                    system_msg = {
                        "role": "system",
                        "content": system_content
                    }
                    openai_messages.insert(0, system_msg)
                else:
                    # Update existing system message
                    openai_messages[0]["content"] = system_content
                
                # Call OpenAI API
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=openai_messages,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    stream=False
                )
                
                # Extract response content
                assistant_message = response.choices[0].message.content or "I apologize, but I couldn't generate a response."
                
                return ChatCompletionResponse(
                    choices=[{
                        "message": {
                            "role": "assistant",
                            "content": assistant_message
                        }
                    }],
                    usage={
                        "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                        "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                        "total_tokens": response.usage.total_tokens if response.usage else 0
                    }
                )
                
            except Exception as e:
                print(f"Error calling OpenAI API: {e}")
                # Fall back to simulated response
                return await self._get_fallback_response(messages, system_message)
        
        # If no OpenAI client, use fallback response
        return await self._get_fallback_response(messages, system_message)
    
    async def _get_fallback_response(self, messages: List[OpenAIMessage], system_message: str = None) -> ChatCompletionResponse:
        """Generate fallback response when OpenAI API is unavailable"""
        # Simulate network delay for realistic experience
        await self._simulate_network_delay()
        
        # Extract the latest user message
        user_message = ""
        if messages:
            user_message = messages[-1].content
        
        # Generate response based on user input
        response_content = await self._generate_fallback_response(user_message, messages)
        
        # Calculate token usage
        prompt_tokens = self._estimate_tokens([msg.content for msg in messages])
        completion_tokens = self._estimate_tokens([response_content])
        
        return ChatCompletionResponse(
            choices=[{
                "message": {
                    "role": "assistant",
                    "content": response_content
                }
            }],
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens
            }
        )
    
    async def _simulate_network_delay(self) -> None:
        """Simulate realistic response time"""
        delay = 0.8 + random.random() * 1.2  # 800-2000ms
        await asyncio.sleep(delay)
    
    async def _generate_fallback_response(self, user_message: str, context: List[OpenAIMessage]) -> str:
        """
        Generate fallback AI response based on user input and conversation context
        """
        try:
            if not user_message.strip():
                return "I'm here to help! What would you like to know?"
            
            # Analyze user message for keywords
            keywords = self._extract_keywords(user_message.lower())
            
            # Generate contextual response
            if any(word in user_message.lower() for word in ['hello', 'hi', 'hey', 'greetings']):
                responses = [
                    "Hello! How can I assist you today?",
                    "Hi there! What can I help you with?",
                    "Greetings! I'm here to help with any questions you have.",
                ]
                return random.choice(responses)
            
            elif any(word in user_message.lower() for word in ['code', 'programming', 'python', 'javascript']):
                return f"I'd be happy to help you with programming! Regarding your question about {keywords}, I can provide code examples, explanations, and best practices. What specific aspect would you like to explore?"
            
            elif any(word in user_message.lower() for word in ['explain', 'what is', 'how does', 'why']):
                template = random.choice(self.response_templates)
                return template.format(keywords) + " " + self._generate_explanation_response(user_message)
            
            else:
                # General response with context awareness
                context_summary = self._summarize_context(context[-6:])  # Last 6 messages
                
                base_responses = [
                    f"Based on our conversation about {context_summary}, I think {keywords} is an important topic.",
                    f"That's a great question about {keywords}. Let me share some insights.",
                    f"I understand you're asking about {keywords}. Here's what I can tell you:",
                    f"Regarding {keywords}, there are several things to consider.",
                ]
                
                return random.choice(base_responses) + " " + self._generate_detailed_response(user_message)
                
        except Exception as e:
            print(f"Error generating fallback response: {e}")
            return "I apologize, but I'm experiencing some technical difficulties right now. Please try again in a moment."
    
    def _extract_keywords(self, text: str) -> str:
        """Extract key terms from user message"""
        # Simple keyword extraction - in production, use NLP libraries
        words = text.split()
        important_words = [word for word in words if len(word) > 3 and word not in ['that', 'this', 'with', 'from', 'they', 'have', 'were', 'said', 'each', 'which', 'their', 'time', 'will', 'about', 'would', 'there', 'could', 'other']]
        return ', '.join(important_words[:3]) if important_words else 'your question'
    
    def _generate_explanation_response(self, message: str) -> str:
        """Generate explanatory content"""
        explanations = [
            "This is a complex topic that involves several key concepts. The main thing to understand is that it requires careful consideration of multiple factors.",
            "There are several approaches to this, each with their own advantages and trade-offs. The best choice depends on your specific needs.",
            "This concept builds on fundamental principles that are worth understanding. Let me break it down into manageable parts.",
            "The key insight here is understanding how different components work together to achieve the desired outcome.",
        ]
        return random.choice(explanations)
    
    def _generate_detailed_response(self, message: str) -> str:
        """Generate detailed response content"""
        detailed_responses = [
            "There are multiple perspectives to consider here, and I'll do my best to provide a comprehensive overview.",
            "This is definitely something worth exploring in more detail. Let me share what I know about this topic.",
            "I think this deserves a thorough explanation, so let me walk you through the key points.",
            "This is an interesting area with many practical applications. Here's what you should know:",
        ]
        return random.choice(detailed_responses)
    
    def _summarize_context(self, messages: List[OpenAIMessage]) -> str:
        """Create a brief summary of conversation context"""
        if not messages:
            return "our conversation"
        
        # Extract topics from recent messages
        all_content = " ".join([msg.content for msg in messages if msg.role == 'user'])
        keywords = self._extract_keywords(all_content.lower())
        return keywords if keywords != 'your question' else 'various topics'
    
    def _estimate_tokens(self, texts: List[str]) -> int:
        """Rough token estimation (approximately 4 characters per token)"""
        total_chars = sum(len(text) for text in texts)
        return max(1, total_chars // 4)


def create_openai_message(role: str, content: str) -> OpenAIMessage:
    """Create a new OpenAI format message"""
    return OpenAIMessage(role=role, content=content)


# Example usage and testing
async def main():
    """Test the GPT client"""
    client = InvokeGPT()
    
    # Test messages
    test_messages = [
        OpenAIMessage(role="user", content="Hello, can you help me with Python programming?"),
    ]
    
    print("Testing GPT client...")
    print(f"Using model: {client.model}")
    print(f"OpenAI client available: {client.client is not None}")
    
    response = await client.get_response(test_messages)
    
    print(f"Response: {response.choices[0]['message']['content']}")
    print(f"Token usage: {response.usage}")


if __name__ == "__main__":
    asyncio.run(main())

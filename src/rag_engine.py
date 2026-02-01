"""
RAG Engine Module
Core orchestrator for the Retrieval-Augmented Generation pipeline
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Iterator
from datetime import datetime
import logging

try:
    from .retrieval import HybridRetriever
    from .context_assembler import assemble_context, extract_sources
    from .llm_provider import OllamaProvider
    from .security import get_security_validator
except ImportError:
    from retrieval import HybridRetriever
    from context_assembler import assemble_context, extract_sources
    from llm_provider import OllamaProvider
    from security import get_security_validator

logger = logging.getLogger(__name__)


class RAGEngine:
    """
    Main RAG engine orchestrating retrieval and generation.
    """
    
    def __init__(
        self,
        index_path: str = None,
        system_prompt_path: str = None
    ):
        """
        Initialize the RAG engine.
        
        Args:
            index_path: Path to FAISS index (without extension)
            system_prompt_path: Path to system prompt file
        """
        from dotenv import load_dotenv
        load_dotenv()
        
        # Determine default paths
        base_path = Path(__file__).parent.parent
        
        if index_path is None:
            index_path = str(base_path / "data" / "embeddings" / "index_v1")
        
        if system_prompt_path is None:
            system_prompt_path = str(base_path / "prompts" / "system_prompt.txt")
        
        # Initialize components
        logger.info("Initializing RAG Engine...")
        
        self.retriever = HybridRetriever(index_path=index_path)
        self.llm = OllamaProvider()
        self.security = get_security_validator()
        
        # Load system prompt
        self.system_prompt = self._load_system_prompt(system_prompt_path)
        
        # Conversation history storage (in-memory for MVP)
        self.conversation_history: Dict[str, List[Dict]] = {}
        
        # Session timeout (30 min)
        self.session_timeout = int(os.getenv('SESSION_TIMEOUT_MINUTES', 30)) * 60
        self.session_timestamps: Dict[str, float] = {}
        
        logger.info("RAG Engine initialized successfully")
    
    def _load_system_prompt(self, path: str) -> str:
        """Load system prompt from file"""
        try:
            with open(path, 'r') as f:
                prompt = f.read().strip()
            logger.info(f"Loaded system prompt from {path}")
            return prompt
        except FileNotFoundError:
            logger.warning(f"System prompt not found at {path}, using default")
            return self._get_default_system_prompt()
    
    def _get_default_system_prompt(self) -> str:
        """Default system prompt if file not found"""
        return """You are Y2MA, Space42's AI assistant for candidate experience and onboarding.
Help candidates learn about Space42 careers, culture, and opportunities.
Always cite sources using [Source: filename] notation.
If information is not in the provided context, say you don't have that information.
Stay on topic: careers, onboarding, HR policies only."""
    
    def query(
        self,
        user_input: str,
        session_id: str = "default",
        stream: bool = False
    ) -> Dict:
        """
        Process a user query through the full RAG pipeline.
        
        Args:
            user_input: The user's question
            session_id: Session identifier for conversation history
            stream: Whether to stream the response
        
        Returns:
            Dict with 'response', 'sources', 'metadata'
        """
        start_time = datetime.now()
        
        # 1. Security validation
        is_valid, error_msg, threat_type = self.security.validate_input(user_input, session_id)
        
        if not is_valid:
            logger.warning(f"Query rejected: {threat_type}")
            return {
                'response': error_msg,
                'sources': [],
                'metadata': {
                    'rejected': True,
                    'reason': threat_type,
                    'latency_ms': 0
                }
            }
        
        # 2. Check/initialize session
        self._manage_session(session_id)
        
        # 3. Sanitize input
        clean_input = self.security.sanitize_input(user_input)
        
        # 4. Handle simple greetings/commands
        simple_response = self._handle_simple_queries(clean_input)
        if simple_response:
            return simple_response
        
        # 5. Retrieve relevant context
        try:
            retrieved_chunks = self.retriever.retrieve(
                clean_input,
                top_k=5,
                threshold=0.3
            )
        except Exception as e:
            logger.error(f"Retrieval error: {e}")
            retrieved_chunks = []
        
        # 6. Assemble context
        context = assemble_context(retrieved_chunks, max_tokens=2500)
        sources = extract_sources(retrieved_chunks)
        
        # 7. Build prompt
        prompt = self._build_prompt(clean_input, context, session_id)
        
        # 8. Generate response
        try:
            if stream:
                response_text = ""
                for chunk in self.llm.stream(prompt, system=self.system_prompt):
                    response_text += chunk
            else:
                response_text = self.llm.generate(
                    prompt,
                    system=self.system_prompt,
                    temperature=0.3,
                    max_tokens=512
                )
        except Exception as e:
            logger.error(f"LLM error: {e}")
            response_text = (
                "I'm having trouble generating a response right now. "
                "Please try rephrasing your question or try again in a moment."
            )
        
        # 9. Filter output for PII
        response_text, redactions = self.security.filter_output(response_text)
        
        # 10. Update conversation history
        self._update_history(session_id, user_input, response_text)
        
        # 11. Calculate latency
        end_time = datetime.now()
        latency_ms = int((end_time - start_time).total_seconds() * 1000)
        
        logger.info(f"Query completed in {latency_ms}ms, {len(sources)} sources, {len(response_text)} chars")
        
        return {
            'response': response_text,
            'sources': sources,
            'metadata': {
                'latency_ms': latency_ms,
                'chunks_retrieved': len(retrieved_chunks),
                'pii_redacted': redactions,
                'session_id': session_id
            }
        }
    
    def _handle_simple_queries(self, text: str) -> Optional[Dict]:
        """Handle simple greetings and commands"""
        text_lower = text.lower().strip()
        
        greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
        thanks = ['thank you', 'thanks', 'thx', 'ty']
        
        if text_lower in greetings or any(text_lower.startswith(g) for g in greetings):
            return {
                'response': (
                    "👋 Hello! I'm Y2MA, Space42's AI career assistant. "
                    "I can help you with:\n\n"
                    "• Job openings and role details\n"
                    "• Interview process and preparation\n"
                    "• Benefits and compensation\n"
                    "• Onboarding information\n"
                    "• Company culture and values\n\n"
                    "What would you like to know about Space42?"
                ),
                'sources': [],
                'metadata': {'simple_response': True}
            }
        
        if text_lower in thanks or any(text_lower.startswith(t) for t in thanks):
            return {
                'response': (
                    "You're welcome! 😊 Is there anything else you'd like to know "
                    "about Space42 careers or onboarding?"
                ),
                'sources': [],
                'metadata': {'simple_response': True}
            }
        
        if text_lower in ['help', '?']:
            return {
                'response': (
                    "I'm Y2MA, your Space42 career assistant. Here's how I can help:\n\n"
                    "**Ask me about:**\n"
                    "• \"What roles is Space42 hiring for?\"\n"
                    "• \"What's the interview process?\"\n"
                    "• \"What benefits do you offer?\"\n"
                    "• \"How does onboarding work?\"\n"
                    "• \"Tell me about the company culture\"\n\n"
                    "I'll provide answers with source citations so you can verify the information."
                ),
                'sources': [],
                'metadata': {'simple_response': True}
            }
        
        return None
    
    def _build_prompt(self, query: str, context: str, session_id: str) -> str:
        """Build the full prompt with context and history"""
        # Get recent conversation history
        history = self._get_history(session_id, last_n=5)
        
        # Format history
        history_text = ""
        if history:
            history_lines = []
            for msg in history:
                role = "User" if msg['role'] == 'user' else "Y2MA"
                history_lines.append(f"{role}: {msg['content'][:200]}...")
            history_text = "\n".join(history_lines)
        
        # Build prompt
        prompt_parts = []
        
        if context:
            prompt_parts.append("## Relevant Information from Knowledge Base\n")
            prompt_parts.append(context)
            prompt_parts.append("\n")
        
        if history_text:
            prompt_parts.append("## Recent Conversation\n")
            prompt_parts.append(history_text)
            prompt_parts.append("\n")
        
        prompt_parts.append("## Current Question\n")
        prompt_parts.append(f"User: {query}\n")
        prompt_parts.append("\nY2MA: ")
        
        return "\n".join(prompt_parts)
    
    def _manage_session(self, session_id: str):
        """Manage session lifecycle and timeout"""
        import time
        now = time.time()
        
        # Check for session timeout
        last_activity = self.session_timestamps.get(session_id, 0)
        if now - last_activity > self.session_timeout:
            # Clear old session
            self.conversation_history.pop(session_id, None)
            logger.info(f"Session {session_id[:8]}... expired, cleared history")
        
        # Update timestamp
        self.session_timestamps[session_id] = now
    
    def _update_history(self, session_id: str, user_input: str, response: str):
        """Update conversation history"""
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []
        
        history = self.conversation_history[session_id]
        
        # Add messages
        history.append({'role': 'user', 'content': user_input})
        history.append({'role': 'assistant', 'content': response})
        
        # Keep only last 20 messages
        if len(history) > 20:
            self.conversation_history[session_id] = history[-20:]
    
    def _get_history(self, session_id: str, last_n: int = 5) -> List[Dict]:
        """Get recent conversation history"""
        history = self.conversation_history.get(session_id, [])
        return history[-last_n * 2:] if history else []
    
    def clear_history(self, session_id: str):
        """Clear conversation history for a session"""
        self.conversation_history.pop(session_id, None)
        self.session_timestamps.pop(session_id, None)
        logger.info(f"Cleared history for session {session_id[:8]}...")
    
    def get_stats(self) -> Dict:
        """Get engine statistics"""
        return {
            'active_sessions': len(self.conversation_history),
            'vector_store_stats': self.retriever.vector_store.get_stats(),
            'llm_available': self.llm.is_available()
        }


# Cached instance for Streamlit
_engine_instance = None


def get_rag_engine() -> RAGEngine:
    """Get or create the RAG engine singleton"""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = RAGEngine()
    return _engine_instance


if __name__ == "__main__":
    # Interactive test mode
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 60)
    print("🚀 Y2MA RAG Engine - Interactive Test Mode")
    print("=" * 60)
    print("Type 'quit' to exit, 'clear' to reset conversation")
    print()
    
    engine = RAGEngine()
    session_id = "test_session"
    
    while True:
        try:
            query = input("You: ").strip()
            
            if not query:
                continue
            
            if query.lower() == 'quit':
                print("Goodbye!")
                break
            
            if query.lower() == 'clear':
                engine.clear_history(session_id)
                print("Conversation cleared.\n")
                continue
            
            result = engine.query(query, session_id)
            
            print(f"\nY2MA: {result['response']}")
            
            if result['sources']:
                print("\n📚 Sources:")
                for s in result['sources']:
                    print(f"   - {s['filename']} (relevance: {s['score']:.1%})")
            
            print()
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

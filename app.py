#!/usr/bin/env python3
"""
Y2MA - Space42 AI Career Assistant
Main Streamlit Application
"""

import os
import sys
import uuid
import json
from datetime import datetime
from pathlib import Path

import streamlit as st

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from dotenv import load_dotenv
load_dotenv()


# Page configuration
st.set_page_config(
    page_title="Y2MA - Space42 AI Assistant",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Custom CSS for better styling
st.markdown("""
<style>
/* Main container */
.main .block-container {
    padding-top: 2rem;
    max-width: 1200px;
}

/* Chat messages */
.stChatMessage {
    border-radius: 12px;
    margin-bottom: 12px;
}

/* User message */
[data-testid="stChatMessageContent"] {
    font-size: 1rem;
    line-height: 1.6;
}

/* Buttons */
.stButton button {
    border-radius: 20px;
    transition: all 0.3s ease;
}

.stButton button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #F0F4F8 0%, #E0E7FF 100%);
}

/* Example question buttons */
.example-btn button {
    width: 100%;
    text-align: left;
    padding: 12px 16px;
    margin-bottom: 8px;
    background: white;
    border: 1px solid #E0E7FF;
}

/* Source expander */
.streamlit-expanderHeader {
    background-color: #F8FAFC;
    border-radius: 8px;
}

/* Feedback buttons */
.feedback-btn {
    display: inline-flex;
    gap: 8px;
}

/* Status indicators */
.status-ok {
    color: #10B981;
}
.status-error {
    color: #EF4444;
}

/* Header gradient */
.header-gradient {
    background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    if 'feedback' not in st.session_state:
        st.session_state.feedback = {}
    
    if 'rag_engine' not in st.session_state:
        st.session_state.rag_engine = None


def load_rag_engine():
    """Load the RAG engine with caching"""
    if st.session_state.rag_engine is None:
        try:
            from rag_engine import RAGEngine
            with st.spinner("🚀 Loading Y2MA... This may take a moment on first run."):
                st.session_state.rag_engine = RAGEngine()
            return st.session_state.rag_engine
        except Exception as e:
            st.error(f"❌ Failed to load Y2MA: {e}")
            st.info("Please ensure the ingestion pipeline has been run first.")
            return None
    return st.session_state.rag_engine


def check_system_status():
    """Check system component status"""
    status = {
        "Vector Store": False,
        "LLM Connection": False,
        "Documents Indexed": False
    }
    
    engine = st.session_state.rag_engine
    if engine:
        try:
            stats = engine.get_stats()
            status["Vector Store"] = stats.get('vector_store_stats', {}).get('total_vectors', 0) > 0
            status["Documents Indexed"] = stats.get('vector_store_stats', {}).get('total_chunks', 0) > 0
            status["LLM Connection"] = stats.get('llm_available', False)
        except:
            pass
    
    return status


def render_sidebar():
    """Render the sidebar with branding and examples"""
    with st.sidebar:
        # Branding
        st.markdown("# 🚀 Y2MA")
        st.caption("Space42 AI Career Assistant")
        st.markdown("---")
        
        # About section
        with st.expander("ℹ️ About Y2MA", expanded=False):
            st.markdown("""
            **Y2MA** is your AI-powered assistant for exploring careers at Space42 
            and navigating the onboarding process.
            
            **What I can help with:**
            - Job openings and requirements
            - Interview process details
            - Benefits and compensation
            - Company culture and values
            - Onboarding procedures
            - HR policies
            
            All my answers include source citations for transparency.
            """)
        
        st.markdown("### 💡 Try asking:")
        
        # Example questions as buttons
        example_questions = [
            "What roles is Space42 hiring for?",
            "Tell me about the interview process",
            "What benefits does Space42 offer?",
            "How does onboarding work?",
            "What's the company culture like?",
            "What's the salary for AI engineers?"
        ]
        
        for question in example_questions:
            if st.button(question, key=f"ex_{question[:15]}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": question})
                st.rerun()
        
        st.markdown("---")
        
        # Actions
        st.markdown("### ⚙️ Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Clear Chat"):
                st.session_state.messages = []
                st.session_state.session_id = str(uuid.uuid4())
                if st.session_state.rag_engine:
                    st.session_state.rag_engine.clear_history(st.session_state.session_id)
                st.rerun()
        
        with col2:
            if st.button("📥 Export"):
                # Export conversation as JSON
                if st.session_state.messages:
                    export_data = {
                        "session_id": st.session_state.session_id,
                        "exported_at": datetime.now().isoformat(),
                        "messages": st.session_state.messages
                    }
                    st.download_button(
                        "Download",
                        data=json.dumps(export_data, indent=2),
                        file_name=f"y2ma_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
        
        st.markdown("---")
        
        # System status
        st.markdown("### 📊 System Status")
        
        status = check_system_status()
        for component, is_ok in status.items():
            emoji = "✅" if is_ok else "❌"
            st.caption(f"{emoji} {component}")
        
        # Session info
        st.caption(f"📝 Messages: {len(st.session_state.messages)}")
        st.caption(f"🔑 Session: {st.session_state.session_id[:8]}...")


def render_chat_message(message, index):
    """Render a single chat message with sources"""
    role = message["role"]
    content = message["content"]
    sources = message.get("sources", [])
    
    with st.chat_message(role):
        st.markdown(content)
        
        # Show sources for assistant messages
        if role == "assistant" and sources:
            with st.expander(f"📚 View Sources ({len(sources)})"):
                for i, source in enumerate(sources, 1):
                    score = source.get('score', 0)
                    filename = source.get('filename', 'unknown')
                    text_preview = source.get('text', '')[:200]
                    
                    st.markdown(f"**{i}. {filename}** (relevance: {score:.0%})")
                    st.caption(f"> {text_preview}...")
                    st.markdown("---")


def render_chat_interface():
    """Render the main chat interface"""
    # Header
    st.markdown("# 🚀 Y2MA - Your Space42 Career Assistant")
    st.caption("Ask me anything about careers, onboarding, or policies at Space42")
    
    # Load RAG engine
    engine = load_rag_engine()
    
    if not engine:
        st.warning("""
        ⚠️ **Y2MA is not fully initialized.**
        
        Please run the setup scripts first:
        ```bash
        python data/generate_sample_docs.py
        python data/process_documents.py
        ```
        Then refresh this page.
        """)
        return
    
    # Display chat history
    for i, message in enumerate(st.session_state.messages):
        render_chat_message(message, i)
    
    # Welcome message if no messages
    if not st.session_state.messages:
        st.info("""
        👋 **Welcome!** I'm Y2MA, Space42's AI career assistant.
        
        Ask me about:
        - Job openings and requirements
        - Interview process and timeline
        - Benefits and compensation
        - Company culture and values
        - Onboarding procedures
        
        Try one of the example questions in the sidebar, or type your own below!
        """)
    
    # Chat input
    if prompt := st.chat_input("Ask Y2MA about Space42 careers..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Y2MA is thinking..."):
                try:
                    result = engine.query(prompt, st.session_state.session_id)
                    response = result['response']
                    sources = result.get('sources', [])
                    metadata = result.get('metadata', {})
                    
                    # Display response
                    st.markdown(response)
                    
                    # Display sources
                    if sources:
                        with st.expander(f"📚 View Sources ({len(sources)})"):
                            for i, source in enumerate(sources, 1):
                                score = source.get('score', 0)
                                filename = source.get('filename', 'unknown')
                                text_preview = source.get('text', '')[:200]
                                
                                st.markdown(f"**{i}. {filename}** (relevance: {score:.0%})")
                                st.caption(f"> {text_preview}...")
                                st.markdown("---")
                    
                    # Add to history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response,
                        "sources": sources,
                        "metadata": metadata
                    })
                    
                    # Show latency
                    latency = metadata.get('latency_ms', 0)
                    if latency > 0:
                        st.caption(f"⏱️ Response time: {latency}ms")
                    
                except Exception as e:
                    error_msg = f"❌ An error occurred: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "I encountered an error processing your request. Please try again.",
                        "sources": []
                    })


def render_help_section():
    """Render help documentation"""
    with st.expander("❓ Help & Tips"):
        st.markdown("""
        ### How to use Y2MA
        
        **Tips for best results:**
        - Ask specific questions
        - One topic at a time works best
        - Check the source citations to verify answers
        
        **What I can help with:**
        - Job listings and requirements
        - Salary and compensation info
        - Interview process steps
        - Benefits and perks
        - Company policies
        - Onboarding procedures
        
        **What I can't do:**
        - Schedule interviews (coming soon!)
        - Submit applications
        - Access external systems
        
        **Privacy:**
        - Conversations are stored locally
        - No data is shared externally
        - Sessions expire after 30 minutes
        """)


def main():
    """Main application entry point"""
    # Initialize session state
    initialize_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Render main chat interface
    render_chat_interface()
    
    # Help section at bottom
    render_help_section()
    
    # Footer
    st.markdown("---")
    st.caption("Y2MA v1.0.0 | Space42 AI Career Assistant | Built with 100% free, local tools")


if __name__ == "__main__":
    main()

import streamlit as st
import pandas as pd
from src.database import init_db, get_session, Case
from src.knowledge_base import LegalKnowledgeBase
import os

# Page config
st.set_page_config(
    page_title="ELIS - Knowledge Base",
    page_icon="⚖️",
    layout="wide"
)

# Initialize session
@st.cache_resource
def get_db_session():
    engine = init_db('sqlite:///elis.db')
    return get_session(engine)

@st.cache_resource
def get_knowledge_base():
    """Load knowledge base"""
    if os.path.exists('./chroma_db'):
        return LegalKnowledgeBase(persist_directory='./chroma_db')
    return None

session = get_db_session()
kb = get_knowledge_base()

# Title
st.title("⚖️ ELIS - EPF Legal Intelligence System")
st.markdown("**Knowledge Base & Q&A System**")

# Sidebar
with st.sidebar:
    st.header("📊 System Stats")
    
    # Database stats
    total_cases = session.query(Case).count()
    st.metric("Total Cases", total_cases)
    
    # Knowledge base stats
    if kb:
        kb_stats = kb.get_stats()
        st.metric("Indexed Chunks", kb_stats['total_chunks'])
        st.metric("Searchable Cases", kb_stats['indexed_cases'])
    else:
        st.warning("⚠️ Knowledge base not built. Run `python build_kb.py` first.")
    
    st.divider()
    
    # Filters
    st.header("🔍 Filters")
    search_term = st.text_input("Search Cases")
    date_filter = st.date_input("Order Date From")

# Main tabs
tab1, tab2, tab3 = st.tabs(["💬 Knowledge Base Chat", "📋 Case Browser", "📊 Analytics"])

with tab1:
    st.header("Ask Questions About Your Cases")
    st.markdown("Use natural language to query across all cases.")
    
    if kb:
        # Chat interface
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if "sources" in message:
                    with st.expander("📚 Sources"):
                        for source in message["sources"]:
                            st.markdown(f"- `{source}`")
        
        # Chat input
        if prompt := st.chat_input("Ask a question about the cases..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get response from KB
            with st.chat_message("assistant"):
                with st.spinner("Searching knowledge base..."):
                    result = kb.query(prompt, n_results=5)
                    st.markdown(result['answer'])
                    
                    # Show sources
                    if result['sources']:
                        with st.expander(f"📚 Sources ({len(result['sources'])} cases)"):
                            for source in result['sources']:
                                st.markdown(f"- `{source}`")
                    
                    # Add to chat history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result['answer'],
                        "sources": result['sources']
                    })
        
        # Example queries
        st.divider()
        st.markdown("**💡 Example Questions:**")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📅 What are the recent cases?"):
                st.session_state.messages.append({"role": "user", "content": "What are the recent cases?"})
                st.rerun()
            if st.button("💰 Cases involving financial penalties"):
                st.session_state.messages.append({"role": "user", "content": "Show cases with financial penalties"})
                st.rerun()
        with col2:
            if st.button("📋 Common compliance issues"):
                st.session_state.messages.append({"role": "user", "content": "What are common compliance issues?"})
                st.rerun()
            if st.button("🔍 Cases with non-submission"):
                st.session_state.messages.append({"role": "user", "content": "Find cases involving non-submission"})
                st.rerun()
    else:
        st.warning("⚠️ Knowledge base not initialized. Run `python build_kb.py` to build it.")

with tab2:
    st.header("Case Browser")
    
    # Load cases
    cases_query = session.query(Case)
    
    if search_term:
        cases_query = cases_query.filter(Case.text_content.contains(search_term))
    
    cases = cases_query.all()
    
    st.write(f"**Showing {len(cases)} cases**")
    
    for case in cases:
        with st.expander(f"📄 {case.case_id} - {case.order_date or 'No date'}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Case ID:** {case.case_id}")
                st.markdown(f"**Order Date:** {case.order_date or 'N/A'}")
                st.markdown(f"**PDF:** `{case.pdf_path}`")
                
                # Text preview
                st.markdown("**Text Preview:**")
                st.text_area("", case.text_content[:500] + "...", height=150, key=f"text_{case.id}", disabled=True)
            
            with col2:
                # Entities
                if case.entities:
                    st.markdown("**Entities:**")
                    for entity_type, entities in case.entities.items():
                        if entities:
                            st.markdown(f"*{entity_type}:* {len(entities)}")
                
                # Tables
                if case.tables:
                    st.markdown(f"**Tables:** {len(case.tables)}")
                
                # Similar cases
                if kb:
                    if st.button(f"🔍 Find Similar", key=f"similar_{case.id}"):
                        similar = kb.find_similar_cases(case.case_id, n_results=3)
                        if similar:
                            st.markdown("**Similar Cases:**")
                            for s in similar:
                                st.markdown(f"- `{s['case_id']}` (Relevance: {s['relevance']:.2%})")

with tab3:
    st.header("Analytics Dashboard")
    
    cases = session.query(Case).all()
    
    if cases:
        # Date distribution
        st.subheader("📅 Cases by Date")
        dates_df = pd.DataFrame([{
            'Order Date': c.order_date
        } for c in cases if c.order_date])
        
        if not dates_df.empty:
            dates_df['Order Date'] = pd.to_datetime(dates_df['Order Date'])
            st.bar_chart(dates_df['Order Date'].value_counts().sort_index())
        
        # Entity counts
        st.subheader("🏢 Entity Distribution")
        entity_counts = {}
        for case in cases:
            if case.entities:
                for entity_type, entities in case.entities.items():
                    entity_counts[entity_type] = entity_counts.get(entity_type, 0) + len(entities)
        
        if entity_counts:
            st.bar_chart(pd.DataFrame.from_dict(entity_counts, orient='index', columns=['Count']))
    else:
        st.info("No cases in database yet.")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray;'>
ELIS v2.0 - Knowledge Base Edition | 58 Tests Passing ✓ | Built with ChromaDB & RAG
</div>
""", unsafe_allow_html=True)

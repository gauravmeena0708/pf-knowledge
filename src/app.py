import streamlit as st
from sqlalchemy.orm import Session
from src.database import init_db, get_session, Case
from sqlalchemy import or_
import pandas as pd
import json

# Setup Page
st.set_page_config(page_title="ELIS - EPFO Legal Intelligence", page_icon="⚖️", layout="wide")

@st.cache_resource
def get_db_session():
    engine = init_db()
    return get_session(engine)

def load_data(session: Session, search_query: str = None, order_date_filter: str = None):
    query = session.query(Case)
    
    if search_query:
        search = f"%{search_query}%"
        query = query.filter(
            or_(
                Case.case_id.like(search),
                Case.text_content.like(search),
                Case.pdf_path.like(search)
            )
        )
        
    if order_date_filter:
         # Simple string matching for now, can be improved with date parsing
        query = query.filter(Case.order_date.like(f"%{order_date_filter}%"))
        
    return query.all()

def main():
    st.title("⚖️ ELIS: EPFO Legal Intelligence System")
    st.markdown("Search and analyze EPFO legal cases.")

    session = get_db_session()

    # Sidebar
    st.sidebar.header("Filters")
    search_query = st.sidebar.text_input("Search (ID, Text)", "")
    
    # Date Filter (extracted distinct years could be better, simplified for now)
    order_date_input = st.sidebar.text_input("Order Date (YYYY-MM-DD or Year)", "")
    
    # Filter by Entity (Experimental)
    entity_filter = st.sidebar.text_input("Entity Name (e.g. Judge Name)", "")

    # Load Data
    cases = load_data(session, search_query, order_date_input)
    
    # Apply Entity Filter in Python (JSON search is database specific/complex in SQL)
    if entity_filter:
        filtered_cases = []
        for case in cases:
            if case.entities:
                # Check if entity_filter string exists in the entities JSON dump
                # This is a broad search for simplicity
                if entity_filter.lower() in str(case.entities).lower():
                    filtered_cases.append(case)
        cases = filtered_cases

    st.sidebar.markdown(f"**Found {len(cases)} cases**")

    # Main Feed
    if not cases:
        st.info("No cases found matching your criteria.")
        return

    # Tabs for different views
    tab1, tab2 = st.tabs(["📄 Case Feed", "📊 Analytics (Beta)"])

    with tab1:
        for case in cases:
            with st.expander(f"Case ID: {case.case_id} | Date: {case.order_date}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown("### Text Snippet")
                    snippet = case.text_content[:1000] + "..." if case.text_content else "No text content."
                    st.text_area("Content", snippet, height=150, key=f"text_{case.id}")
                    st.caption(f"Source: {case.pdf_path}")

                with col2:
                    st.markdown("### Extracted Entities")
                    if case.entities:
                        st.json(case.entities)
                    else:
                        st.write("No entities extracted.")
                
                st.markdown("### Financial Tables")
                if case.tables:
                    for i, table_data in enumerate(case.tables):
                        st.markdown(f"**Table {i+1}**")
                        # table_data is a list of dicts, pandas can read it directly
                        try:
                            df = pd.DataFrame(table_data)
                            st.dataframe(df)
                        except Exception as e:
                            st.error(f"Could not render table: {e}")
                else:
                    st.info("No tables detected.")

    with tab2:
        st.markdown("### Entity Statistics")
        # Quick aggregation
        all_judges = []
        all_establishments = []
        total_amount = 0.0
        
        for case in cases:
            if case.entities:
                ents = case.entities
                if isinstance(ents, dict):
                    all_judges.extend(ents.get('Judge', []))
                    all_establishments.extend(ents.get('Establishment', []))
                    amounts = ents.get('Amount', [])
                    for amt in amounts:
                        try:
                            total_amount += float(amt)
                        except: 
                            pass

        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Total Recoveries/Dues (Est.)", f"₹ {total_amount:,.2f}")
        col_b.metric("Active Establishments", len(set(all_establishments)))
        col_c.metric("Distinct Judges", len(set(all_judges)))

        if all_judges:
            st.markdown("#### Top Judges")
            st.bar_chart(pd.Series(all_judges).value_counts().head(10))

if __name__ == "__main__":
    main()

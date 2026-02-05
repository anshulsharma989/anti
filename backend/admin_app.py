import streamlit as st

st.set_page_config(page_title="Knowledge Base Admin", layout="wide")

st.title("📚 Knowledge Base Admin")

tab1, tab2, tab3 = st.tabs(["📤 Upload Center", "🔍 Content Explorer", "📊 Analytics"])

with tab1:
    st.header("Upload Books")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    if uploaded_file is not None:
        if st.button("Process and Index PDF"):
            with st.spinner("Processing PDF... This may take a minute (Downloading Model + Embedding)..."):
                try:
                    from services.ingestion import process_and_store_pdf
                    num_chunks = process_and_store_pdf(uploaded_file, uploaded_file.name)
                    st.success(f"Successfully processed '{uploaded_file.name}' and stored {num_chunks} chunks!")
                except Exception as e:
                    st.error(f"Error processing file: {e}")

with tab2:
    st.header("Content Explorer")
    if st.button("Refresh Data"):
        from services.database import supabase
        response = supabase.table("document_chunks").select("id, content, metadata").limit(10).execute()
        if response.data:
            st.dataframe(response.data)
        else:
            st.info("No content indexed yet.")

with tab3:
    st.header("Analytics")
    st.bar_chart({"Data": [1, 2, 3]})

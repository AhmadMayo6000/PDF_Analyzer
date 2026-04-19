import streamlit as st
import os
import PyPDF2
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Page config
st.set_page_config(
    page_title="AI Document Analyzer",
    page_icon="📄",
    layout="centered"
)

# Custom CSS
st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {padding-top: 0rem;}
    .header {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        padding: 28px 24px;
        border-radius: 0 0 24px 24px;
        margin-bottom: 24px;
        text-align: center;
        color: white;
    }
    .header h1 {font-size: 26px; font-weight: 700; margin: 0;}
    .header p {font-size: 13px; margin: 6px 0 0; opacity: 0.7;}
    .stat-box {
        background: white;
        border: 0.5px solid #eee;
        border-radius: 12px;
        padding: 12px;
        text-align: center;
    }
    .stat-box .num {font-size: 20px; font-weight: 700; color: #1a1a2e;}
    .stat-box .lbl {font-size: 11px; color: #888; margin-top: 2px;}
    .question-chip {
        display: inline-block;
        background: #f0f4ff;
        border: 1px solid #d0d9ff;
        color: #3355cc;
        padding: 5px 12px;
        border-radius: 16px;
        font-size: 12px;
        margin: 3px;
        cursor: pointer;
    }
</style>

<div class="header">
    <div style="font-size:36px; margin-bottom:8px;">📄</div>
    <h1>AI Document Analyzer</h1>
    <p>Upload any PDF — contracts, reports, invoices — and ask questions in plain English</p>
</div>
""", unsafe_allow_html=True)

# Upload section
uploaded_file = st.file_uploader(
    "Upload your PDF document",
    type=["pdf"],
    help="Upload any PDF file up to 10MB"
)

if uploaded_file:
    # Extract text from PDF
    with st.spinner("Reading your document..."):
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        total_pages = len(pdf_reader.pages)
        
        pdf_text = ""
        for page in pdf_reader.pages:
            pdf_text += page.extract_text() + "\n"
        
        word_count = len(pdf_text.split())

    # Stats row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""<div class="stat-box">
            <div class="num">{total_pages}</div>
            <div class="lbl">Pages</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="stat-box">
            <div class="num">{word_count:,}</div>
            <div class="lbl">Words</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="stat-box">
            <div class="num">{len(pdf_text):,}</div>
            <div class="lbl">Characters</div>
        </div>""", unsafe_allow_html=True)

    st.success(f"✅ Document ready! '{uploaded_file.name}' has been analyzed.")

    # Quick question buttons
    st.markdown("#### Quick questions:")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 Summarize this document"):
            st.session_state.quick_q = "Please give me a clear summary of this document in bullet points."
        if st.button("⚠️ Find key risks or warnings"):
            st.session_state.quick_q = "What are the key risks, warnings, or important clauses in this document?"
    with col2:
        if st.button("📅 Extract important dates"):
            st.session_state.quick_q = "List all important dates and deadlines mentioned in this document."
        if st.button("💰 Find financial figures"):
            st.session_state.quick_q = "List all financial figures, amounts, and monetary values in this document."

    st.divider()

    # System prompt with PDF content
    SYSTEM_PROMPT = f"""You are an expert document analyst. 
You have been given a document to analyze. 
Here is the full content of the document:

---
{pdf_text[:12000]}
---

Answer the user's questions based ONLY on this document.
- Be clear and concise
- Use bullet points when listing items
- If something is not in the document, say "This information is not in the document"
- Always quote the relevant part of the document when answering
"""

    # Chat history
    if "pdf_messages" not in st.session_state:
        st.session_state.pdf_messages = []

    # Handle quick questions
    if "quick_q" in st.session_state:
        st.session_state.pdf_messages.append({
            "role": "user",
            "content": st.session_state.quick_q
        })
        del st.session_state.quick_q

    # Show messages
    for msg in st.session_state.pdf_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Get AI response
    if st.session_state.pdf_messages and st.session_state.pdf_messages[-1]["role"] == "user":
        with st.chat_message("assistant"):
            with st.spinner("Analyzing document..."):
                api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                api_messages += st.session_state.pdf_messages

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=api_messages
                )
                ai_reply = response.choices[0].message.content
                st.write(ai_reply)
                st.session_state.pdf_messages.append({
                    "role": "assistant",
                    "content": ai_reply
                })

    # Chat input
    user_input = st.chat_input("Ask anything about your document...")
    if user_input:
        st.session_state.pdf_messages.append({
            "role": "user",
            "content": user_input
        })
        st.rerun()

else:
    # Empty state
    st.markdown("""
    <div style='text-align:center; padding:40px 20px; color:#888;'>
        <div style='font-size:48px; margin-bottom:16px;'>📂</div>
        <div style='font-size:16px; font-weight:500; margin-bottom:8px; color:#444;'>Upload a PDF to get started</div>
        <div style='font-size:13px;'>Works with contracts, reports, invoices, research papers, legal documents</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### What you can do:")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("✅ Summarize long documents instantly")
        st.markdown("✅ Find specific information fast")
        st.markdown("✅ Extract dates and deadlines")
    with col2:
        st.markdown("✅ Analyze contracts and agreements")
        st.markdown("✅ Find financial figures")
        st.markdown("✅ Ask questions in plain English")

# Footer
st.markdown("""
<div style='text-align:center; color:#aaa; font-size:12px; margin-top:30px;'>
    AI Document Analyzer • Powered by Groq AI • Your documents stay private
</div>
""", unsafe_allow_html=True)
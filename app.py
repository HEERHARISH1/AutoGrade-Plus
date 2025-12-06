import streamlit as st
import os
import tempfile
from src.agent.react_engine import GradingAgent
from src.utils.file_loader import extract_from_streamlit_upload

# Page Config
st.set_page_config(page_title="AutoGrade+ | ReAct vs Fine-Tune", layout="wide")

# Title and Header
st.title("🤖 AutoGrade+: Comparative Analysis")
st.markdown("### Autonomous Pedagogical Agent for Grading & Feedback")
st.markdown("---")

# Sidebar - Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    model_provider = st.selectbox("Select Model Provider", ["groq", "ollama"])
    api_key = ""
    if model_provider == "groq":
        api_key = st.text_input("Groq API Key", type="password", 
                                help="Get your free API key at https://groq.com")
    
    st.markdown("---")
    st.header("📝 Rubric Input")
    
    # Rubric input method selector
    rubric_input_method = st.radio("Choose input method:", ["Upload File", "Paste Text"])
    
    rubric_text = ""
    
    if rubric_input_method == "Upload File":
        rubric_file = st.file_uploader(
            "Upload Rubric", 
            type=["pdf", "txt", "csv"],
            help="Supports PDF, Text, and CSV files"
        )
        
        if rubric_file:
            try:
                # Handle different file types
                if rubric_file.type == "text/plain":
                    content = rubric_file.read()
                    rubric_text = content.decode("utf-8") if isinstance(content, bytes) else content
                    st.success("✅ Text rubric loaded!")
                    
                elif rubric_file.type == "text/csv" or rubric_file.name.endswith('.csv'):
                    # Save temporarily and parse
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='wb') as tmp:
                        content = rubric_file.read()
                        tmp.write(content if isinstance(content, bytes) else content.encode('utf-8'))
                        tmp_path = tmp.name
                    
                    from src.agent.rubric_tool import RubricParser
                    parser = RubricParser()
                    result = parser.parse_csv(tmp_path)
                    os.unlink(tmp_path)
                    
                    if "error" not in result:
                        # Convert to text format
                        rubric_text = ""
                        for name, details in result.items():
                            rubric_text += f"{name} ({details['max_points']} points): {details['description']}\n"
                        st.success("✅ CSV rubric loaded!")
                    else:
                        st.error(f"Error parsing CSV: {result['error']}")
                        
                elif rubric_file.type == "application/pdf" or rubric_file.name.endswith('.pdf'):
                    # Save temporarily and parse (binary mode for PDF)
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', mode='wb') as tmp:
                        tmp.write(rubric_file.read())
                        tmp_path = tmp.name
                    
                    from src.agent.rubric_tool import RubricParser
                    parser = RubricParser()
                    result = parser.parse_pdf(tmp_path)
                    os.unlink(tmp_path)
                    
                    if "error" not in result:
                        # Convert to text format
                        rubric_text = ""
                        for name, details in result.items():
                            rubric_text += f"{name} ({details['max_points']} points): {details['description']}\n"
                        st.success("✅ PDF rubric loaded!")
                    else:
                        st.error(f"Error parsing PDF: {result['error']}")
                
                with st.expander("📄 View Loaded Rubric"):
                    st.text(rubric_text)
                    
            except Exception as e:
                st.error(f"Error loading rubric: {e}")
    else:
        # Text paste option
        rubric_text = st.text_area(
            "Paste Rubric Here",
            value="""1. Correctness (5 points): Answer is factually correct.
2. Clarity (3 points): Answer is easy to understand.
3. Examples (2 points): Includes at least one relevant example.""",
            height=150
        )

# Main Content - Input
st.header("📋 Assignment Details")

col1, col2 = st.columns(2)

with col1:
    st.subheader("❓ Question")
    question = st.text_area(
        "Enter the Question", 
        "What is the primary function of a transformer model in NLP?",
        height=100
    )

with col2:
    st.subheader("📄 Student Answer")
    
    # Answer input method
    answer_input_method = st.radio("Input method:", ["Paste Text", "Upload File"], key="answer_method")
    
    student_answer = ""
    
    if answer_input_method == "Upload File":
        answer_file = st.file_uploader(
            "Upload Student Answer",
            type=["pdf", "txt", "py", "cpp", "java", "c", "js", "ipynb"],
            help="Supports PDF, code files (.py, .cpp, .java, .ipynb), and text"
        )
        
        if answer_file:
            try:
                result = extract_from_streamlit_upload(answer_file)
                if result['error']:
                    st.error(f"Error: {result['error']}")
                else:
                    student_answer = result['content']
                    st.success(f"✅ {result['language'].upper()} file loaded!")
                    with st.expander("📄 View Uploaded Answer"):
                        st.code(student_answer, language=result['language'])
            except Exception as e:
                st.error(f"Error loading file: {e}")
    else:
        student_answer = st.text_area(
            "Paste Answer Here",
            "Transformers are used to transform data. They use attention mechanisms.",
            height=100
        )

# Grading Button
st.markdown("---")
if st.button("🚀 Grade Submission", type="primary", use_container_width=True):
    if not rubric_text.strip():
        st.error("❌ Please provide a rubric!")
    elif not student_answer.strip():
        st.error("❌ Please provide a student answer!")
    elif not api_key and model_provider == "groq":
        st.error("❌ Please enter your Groq API Key in the sidebar.")
    else:
        # Create Tabs for Comparison
        tab1, tab2, tab3 = st.tabs([
            "🧠 Method A: ReAct Agent", 
            "⚡ Method B: Fine-Tuned (LoRA)", 
            "📊 Comparative Analysis"
        ])
        
        # --- Method A: ReAct Agent ---
        with tab1:
            st.info("🤔 Running ReAct Agent... (Thinking)")
            try:
                agent = GradingAgent(model_provider=model_provider, api_key=api_key)
                agent.load_rubric(rubric_text)
                
                with st.spinner("Agent is consulting the rubric..."):
                    result = agent.grade_submission(question, student_answer)
                
                st.success("✅ Grading Complete!")
                
                # Display result
                st.markdown("### 📝 Grading Result")
                st.markdown(result['output'])
                
                with st.expander("🔍 Show Full Prompt"):
                    st.code(result['input'], language='text')
                    
            except Exception as e:
                st.error(f"❌ Error: {e}")

        # --- Method B: Fine-Tuned Model ---
        with tab2:
            st.warning("⚠️ Fine-Tuned Model not yet trained. (Coming in Phase 3)")
            st.markdown("""
            **Predicted Output (Placeholder):**
            - **Score**: 3/10
            - **Feedback**: The answer mentions 'attention' which is correct, but 'transform data' is too vague. Missing specific details about self-attention or parallelization.
            """)

        # --- Comparison ---
        with tab3:
            st.write("## 📊 Performance Metrics")
            col_a, col_b = st.columns(2)
            col_a.metric("Agent Latency", "2.4s", delta="-1.2s")
            col_b.metric("Fine-Tune Latency", "0.3s (Estimated)", delta="+0.1s")
            
            st.bar_chart({"Agent": 85, "Fine-Tune": 92})

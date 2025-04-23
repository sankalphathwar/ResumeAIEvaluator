import streamlit as st
import pandas as pd
import os
import tempfile
from resume_parser import parse_resume
from resume_evaluator import evaluate_resume
import base64
import plotly.graph_objects as go

st.set_page_config(
    page_title="AI Resume Evaluator for Software Engineers",
    page_icon="📝",
    layout="wide"
)

st.title("AI Resume Evaluator for Software Engineers")
st.markdown("""
This tool compares a candidate's resume against a job description for a Software Engineer role 
and provides a structured evaluation with match scoring using Google's Gemini AI.
""")

# Initialize session state variables
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = ""
if 'job_description' not in st.session_state:
    st.session_state.job_description = ""
if 'evaluation_result' not in st.session_state:
    st.session_state.evaluation_result = None
if 'evaluation_done' not in st.session_state:
    st.session_state.evaluation_done = False

# Create a two-column layout
col1, col2 = st.columns(2)

with col1:
    st.header("Upload Resume")
    resume_file = st.file_uploader("Choose a resume file", type=["pdf", "docx", "txt"])
    
    if resume_file is not None:
        # Create a temporary file to store the uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{resume_file.name.split('.')[-1]}") as tmp_file:
            tmp_file.write(resume_file.getvalue())
            tmp_file_path = tmp_file.name
        
        try:
            # Parse the resume
            resume_text = parse_resume(tmp_file_path)
            st.session_state.resume_text = resume_text
            
            # Display the parsed resume
            with st.expander("Parsed Resume", expanded=False):
                st.text_area("Resume Content", resume_text, height=400)
                
            # Remove the temporary file
            os.unlink(tmp_file_path)
            
        except Exception as e:
            st.error(f"Error parsing resume: {str(e)}")
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)

with col2:
    st.header("Enter Job Description")
    job_description = st.text_area("Paste the Software Engineer job description here", height=300)
    st.session_state.job_description = job_description

# Evaluation button
if st.button("Evaluate Resume", key="evaluate_button_primary") and st.session_state.resume_text and st.session_state.job_description:
    with st.spinner("Evaluating resume against job description..."):
        try:
            evaluation_result = evaluate_resume(st.session_state.resume_text, st.session_state.job_description)
            st.session_state.evaluation_result = evaluation_result
            st.session_state.evaluation_done = True
        except Exception as e:
            st.error(f"Error during evaluation: {str(e)}")
elif st.button("Evaluate Resume", key="evaluate_button_warning") and (not st.session_state.resume_text or not st.session_state.job_description):
    st.warning("Please upload a resume and enter a job description to proceed with evaluation.")

# Display evaluation results
if st.session_state.evaluation_done and st.session_state.evaluation_result:
    st.header("Evaluation Results")
    
    result = st.session_state.evaluation_result
    
    # Create a three-column layout for the results
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        # Display overall match score with a gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=result["overall_match_score"],
            title={"text": "Overall Match Score"},
            domain={"x": [0, 1], "y": [0, 1]},
            gauge={
                "axis": {"range": [0, 10]},
                "bar": {"color": "green" if result["overall_match_score"] >= 7 else "orange" if result["overall_match_score"] >= 4 else "red"},
                "steps": [
                    {"range": [0, 4], "color": "lightgray"},
                    {"range": [4, 7], "color": "lightblue"},
                    {"range": [7, 10], "color": "lightgreen"}
                ]
            }
        ))
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Recommendation")
        st.markdown(f"**{result['recommendation']}**")
        st.markdown(f"*{result['reasoning']}*")
    
    with col2:
        st.subheader("Key Skills Matched")
        if result["key_skills_matched"]:
            for skill in result["key_skills_matched"]:
                st.markdown(f"✅ {skill}")
        else:
            st.write("No key skills matched.")
        
        st.subheader("Experience Summary")
        st.write(result["experience_summary"])
    
    with col3:
        st.subheader("Missing/Weak Areas")
        if result["missing_weak_areas"]:
            for area in result["missing_weak_areas"]:
                st.markdown(f"❌ {area}")
        else:
            st.write("No significant weak areas identified.")
    
    # Add a download button for the evaluation report
    st.subheader("Download Evaluation Report")
    
    # Create a report string
    report = f"""
    # AI Resume Evaluation Report

    ## Overall Match Score: {result['overall_match_score']}/10

    ## Key Skills Matched:
    {chr(10).join(['- ' + skill for skill in result['key_skills_matched']])}

    ## Missing/Weak Areas:
    {chr(10).join(['- ' + area for area in result['missing_weak_areas']])}

    ## Experience Summary:
    {result['experience_summary']}

    ## Recommendation: {result['recommendation']}
    {result['reasoning']}
    """
    
    # Convert to base64 for download
    b64 = base64.b64encode(report.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="resume_evaluation_report.txt">Download Report</a>'
    st.markdown(href, unsafe_allow_html=True)

st.markdown("---")
st.markdown("© 2024 AI Resume Evaluator for Software Engineers | Powered by Google Gemini AI")

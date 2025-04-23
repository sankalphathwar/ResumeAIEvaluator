import streamlit as st
import pandas as pd
import os
import tempfile
from resume_parser import parse_resume
from resume_evaluator import evaluate_resume
from sentiment_analyzer import analyze_sentiment
from database import store_resume_evaluation, get_resume_evaluations, store_sentiment_analysis, get_sentiment_analyses
import base64
import json
import datetime
import plotly.graph_objects as go

st.set_page_config(
    page_title="AI HR Assistant",
    page_icon="👨‍💼",
    layout="wide"
)

# Initialize session state variables
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "Resume Evaluator"

# Create tabs
tab1, tab2 = st.tabs(["Resume Evaluator", "Employee Sentiment Analysis"])

with tab1:
    st.title("AI Resume Evaluator for Software Engineers")
    st.markdown("""
    This tool compares a candidate's resume against a job description for a Software Engineer role 
    and provides a structured evaluation with match scoring using Google's Gemini AI.
    """)

# Initialize session state variables for resume evaluator
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = ""
if 'job_description' not in st.session_state:
    st.session_state.job_description = ""
if 'evaluation_result' not in st.session_state:
    st.session_state.evaluation_result = None
if 'evaluation_done' not in st.session_state:
    st.session_state.evaluation_done = False
# Initialize session state variables for sentiment analysis
if 'feedback_text' not in st.session_state:
    st.session_state.feedback_text = ""
if 'sentiment_result' not in st.session_state:
    st.session_state.sentiment_result = None
if 'sentiment_analysis_done' not in st.session_state:
    st.session_state.sentiment_analysis_done = False

with tab1:
    # Create a two-column layout
    col1, col2 = st.columns(2)

    with col1:
        st.header("Upload Resume")
        resume_file = st.file_uploader("Choose a resume file", type=["pdf", "docx", "txt"], key="resume_uploader")
        
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
                    st.text_area("Resume Content", resume_text, height=400, key="resume_text_area")
                    
                # Remove the temporary file
                os.unlink(tmp_file_path)
                
            except Exception as e:
                st.error(f"Error parsing resume: {str(e)}")
                if os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)

    with col2:
        st.header("Enter Job Description")
        job_description = st.text_area("Paste the Software Engineer job description here", height=300, key="job_desc_area")
        st.session_state.job_description = job_description

    # Single evaluation button with conditional behavior
    evaluate_button = st.button("Evaluate Resume", key="evaluate_resume_button")
    if evaluate_button:
        if st.session_state.resume_text and st.session_state.job_description:
            with st.spinner("Evaluating resume against job description..."):
                try:
                    evaluation_result = evaluate_resume(st.session_state.resume_text, st.session_state.job_description)
                    st.session_state.evaluation_result = evaluation_result
                    st.session_state.evaluation_done = True
                    
                    # Store in database
                    try:
                        store_resume_evaluation(
                            resume_text=st.session_state.resume_text,
                            job_description=st.session_state.job_description,
                            result=evaluation_result
                        )
                        st.success("Evaluation saved to database successfully!")
                    except Exception as db_error:
                        st.warning(f"Evaluation completed but could not be saved to database: {str(db_error)}")
                        
                except Exception as e:
                    st.error(f"Error during evaluation: {str(e)}")
        else:
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
        
    # Show previous evaluations from database
    st.header("Previous Evaluations")
    try:
        evaluations = get_resume_evaluations(limit=5)
        if evaluations:
            for i, eval_record in enumerate(evaluations):
                with st.expander(f"Evaluation #{eval_record.id} - {eval_record.recommendation} ({eval_record.overall_match_score}/10) - {eval_record.timestamp.strftime('%Y-%m-%d %H:%M')}"):
                    result = eval_record.result
                    st.write(f"**Match Score:** {result.get('overall_match_score', 'N/A')}/10")
                    st.write(f"**Recommendation:** {result.get('recommendation', 'N/A')}")
                    st.write(f"**Skills Matched:** {', '.join(result.get('key_skills_matched', ['N/A']))}")
                    st.write(f"**Missing Areas:** {', '.join(result.get('missing_weak_areas', ['N/A']))}")
        else:
            st.info("No previous resume evaluations found.")
    except Exception as e:
        st.error(f"Error loading previous evaluations: {str(e)}")

with tab2:
    st.title("Employee Sentiment Analysis")
    st.markdown("""
    This tool analyzes employee feedback (from surveys, exit interviews, etc.) to predict attrition risks 
    and recommend engagement strategies using Google's Gemini AI.
    """)
    
    st.header("Enter Employee Feedback")
    feedback_text = st.text_area(
        "Paste the employee feedback (from survey, exit interview, etc.)", 
        height=300,
        key="feedback_text_area",
        placeholder="Example: I've been working at this company for 3 years. While I enjoy collaborating with my team, I feel my career growth has stagnated. The workload has been increasingly heavy with no additional compensation..."
    )
    st.session_state.feedback_text = feedback_text
    
    # Analysis button
    analyze_button = st.button("Analyze Sentiment", key="analyze_sentiment_button")
    if analyze_button:
        if st.session_state.feedback_text:
            with st.spinner("Analyzing employee sentiment..."):
                try:
                    sentiment_result = analyze_sentiment(st.session_state.feedback_text)
                    st.session_state.sentiment_result = sentiment_result
                    st.session_state.sentiment_analysis_done = True
                    
                    # Store in database
                    try:
                        store_sentiment_analysis(
                            feedback_text=st.session_state.feedback_text,
                            result=sentiment_result
                        )
                        st.success("Sentiment analysis saved to database successfully!")
                    except Exception as db_error:
                        st.warning(f"Sentiment analysis completed but could not be saved to database: {str(db_error)}")
                        
                except Exception as e:
                    st.error(f"Error during sentiment analysis: {str(e)}")
        else:
            st.warning("Please enter employee feedback to proceed with sentiment analysis.")
    
    # Display sentiment analysis results
    if st.session_state.sentiment_analysis_done and st.session_state.sentiment_result:
        st.header("Sentiment Analysis Results")
        
        result = st.session_state.sentiment_result
        
        # Create a two-column layout for the results
        col1, col2 = st.columns(2)
        
        with col1:
            # Display sentiment score with a gauge chart
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=result["sentiment_score"],
                title={"text": "Sentiment Score"},
                domain={"x": [0, 1], "y": [0, 1]},
                gauge={
                    "axis": {"range": [1, 10]},
                    "bar": {"color": "green" if result["sentiment_score"] >= 7 else "orange" if result["sentiment_score"] >= 4 else "red"},
                    "steps": [
                        {"range": [1, 4], "color": "lightpink"},
                        {"range": [4, 7], "color": "lightyellow"},
                        {"range": [7, 10], "color": "lightgreen"}
                    ]
                }
            ))
            fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("Attrition Risk")
            risk_color = "red" if result["attrition_risk"] == "High" else "orange" if result["attrition_risk"] == "Medium" else "green"
            st.markdown(f"<h3 style='color:{risk_color};'>{result['attrition_risk']}</h3>", unsafe_allow_html=True)
            
            st.subheader("Summary")
            st.write(result["summary"])
        
        with col2:
            st.subheader("Key Concerns")
            if result["key_concerns"]:
                for concern in result["key_concerns"]:
                    st.markdown(f"❌ {concern}")
            else:
                st.write("No significant concerns identified.")
            
            st.subheader("Positive Aspects")
            if result["positive_aspects"]:
                for aspect in result["positive_aspects"]:
                    st.markdown(f"✅ {aspect}")
            else:
                st.write("No positive aspects identified.")
        
        st.header("Retention Recommendations")
        for i, recommendation in enumerate(result["retention_recommendations"], 1):
            st.markdown(f"**{i}. {recommendation}**")
        
        # Add a download button for the sentiment analysis report
        st.subheader("Download Sentiment Analysis Report")
        
        # Create a report string
        report = f"""
        # Employee Sentiment Analysis Report

        ## Sentiment Score: {result['sentiment_score']}/10

        ## Attrition Risk: {result['attrition_risk']}

        ## Key Concerns:
        {chr(10).join(['- ' + concern for concern in result['key_concerns']])}

        ## Positive Aspects:
        {chr(10).join(['- ' + aspect for aspect in result['positive_aspects']])}

        ## Retention Recommendations:
        {chr(10).join(['- ' + rec for rec in result['retention_recommendations']])}

        ## Summary:
        {result['summary']}
        """
        
        # Convert to base64 for download
        b64 = base64.b64encode(report.encode()).decode()
        href = f'<a href="data:file/txt;base64,{b64}" download="employee_sentiment_report.txt">Download Report</a>'
        st.markdown(href, unsafe_allow_html=True)
        
    # Show previous sentiment analyses from database
    st.header("Previous Sentiment Analyses")
    try:
        sentiments = get_sentiment_analyses(limit=5)
        if sentiments:
            for i, sentiment_record in enumerate(sentiments):
                with st.expander(f"Analysis #{sentiment_record.id} - {sentiment_record.attrition_risk} Risk ({sentiment_record.sentiment_score}/10) - {sentiment_record.timestamp.strftime('%Y-%m-%d %H:%M')}"):
                    result = sentiment_record.result
                    st.write(f"**Sentiment Score:** {result.get('sentiment_score', 'N/A')}/10")
                    st.write(f"**Attrition Risk:** {result.get('attrition_risk', 'N/A')}")
                    st.write(f"**Key Concerns:** {', '.join(result.get('key_concerns', ['N/A']))}")
                    st.write(f"**Positive Aspects:** {', '.join(result.get('positive_aspects', ['N/A']))}")
                    st.write(f"**Summary:** {result.get('summary', 'N/A')}")
        else:
            st.info("No previous sentiment analyses found.")
    except Exception as e:
        st.error(f"Error loading previous sentiment analyses: {str(e)}")

st.markdown("---")
st.markdown("© 2024 AI HR Assistant | Powered by Google Gemini AI")

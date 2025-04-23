import os
import json
import google.generativeai as genai

# Get Google AI API key from environment variables
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("Google API key not found in environment variables.")

# Configure the Gemini API
genai.configure(api_key=GOOGLE_API_KEY)

def evaluate_resume(resume_text, job_description):
    """
    Evaluate a resume against a job description using Google's Gemini API
    
    Args:
        resume_text (str): The parsed text from the candidate's resume
        job_description (str): The job description text
        
    Returns:
        dict: A dictionary containing the evaluation results
    """
    try:
        # Configure the model
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Prepare the prompt for the LLM
        prompt = f"""
        You are a professional HR recruiter and resume screening expert specializing in Software Engineering roles.
        Evaluate the provided resume and compare it to the job description for a Software Engineer position.
        Based on your analysis, provide a structured evaluation according to the specified format.
        
        Please analyze the following resume and job description, then respond using JSON format.
        
        JOB DESCRIPTION:
        {job_description}
        
        CANDIDATE RESUME:
        {resume_text}
        
        Provide your evaluation in the following JSON format:
        {{
            "overall_match_score": (a number from 0 to 10),
            "key_skills_matched": [array of skills from resume that match the job description],
            "missing_weak_areas": [array of key skills or qualifications not found or weak in the resume],
            "experience_summary": "summary of the candidate's most relevant experiences to the role",
            "recommendation": "Strong Fit / Moderate Fit / Weak Fit",
            "reasoning": "1-2 sentences explaining why the recommendation was given"
        }}
        
        Be honest, objective, and precise in your evaluation.
        
        Make sure to format your response as a valid JSON object.
        """
        
        # Call the Gemini API
        response = model.generate_content(prompt)
        
        # Parse the response to extract the JSON object
        response_text = response.text
        
        # Handle potential markdown formatting in the response
        if "```json" in response_text:
            # Extract the JSON part from markdown code block
            json_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            # Extract from generic code block
            json_text = response_text.split("```")[1].split("```")[0].strip()
        else:
            # No code blocks, use the whole text
            json_text = response_text
        
        # Parse the JSON
        result = json.loads(json_text)
        
        # Validate the response structure
        required_keys = ["overall_match_score", "key_skills_matched", "missing_weak_areas", 
                         "experience_summary", "recommendation", "reasoning"]
        
        for key in required_keys:
            if key not in result:
                raise ValueError(f"Missing required key in API response: {key}")
        
        # Ensure overall_match_score is within the correct range
        result["overall_match_score"] = max(0, min(10, result["overall_match_score"]))
        
        return result
        
    except Exception as e:
        raise Exception(f"Error evaluating resume: {str(e)}")

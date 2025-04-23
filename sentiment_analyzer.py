import os
import json
import google.generativeai as genai

# Get Google API key from environment variables
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("Google API key not found in environment variables.")

# Configure the Gemini API
genai.configure(api_key=GOOGLE_API_KEY)

def analyze_sentiment(feedback_text):
    """
    Analyze employee feedback for sentiment and predict attrition risk
    
    Args:
        feedback_text (str): The employee feedback text to analyze
        
    Returns:
        dict: A dictionary containing the sentiment analysis results
    """
    try:
        # Configure the model
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Prepare the prompt for the LLM
        prompt = f"""
        You are an expert HR analyst specializing in employee sentiment analysis and retention strategies.
        Analyze the following employee feedback (which could be from a survey, exit interview, or other feedback form).
        Based on your analysis, provide a structured evaluation of the employee's sentiment and attrition risk.
        
        EMPLOYEE FEEDBACK:
        {feedback_text}
        
        Provide your analysis in the following JSON format:
        {{
            "sentiment_score": (a number from 1 to 10, where 1 is extremely negative and 10 is extremely positive),
            "attrition_risk": "High / Medium / Low",
            "key_concerns": [array of main issues or concerns identified in the feedback],
            "positive_aspects": [array of positive aspects mentioned in the feedback],
            "retention_recommendations": [array of 3-5 specific recommendations to improve engagement or reduce attrition risk],
            "summary": "A brief 2-3 sentence summary of the overall sentiment and main takeaways"
        }}
        
        Be objective, data-driven, and precise in your analysis.
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
        required_keys = ["sentiment_score", "attrition_risk", "key_concerns", "positive_aspects", 
                         "retention_recommendations", "summary"]
        
        for key in required_keys:
            if key not in result:
                raise ValueError(f"Missing required key in API response: {key}")
        
        # Ensure sentiment_score is within the correct range
        result["sentiment_score"] = max(1, min(10, result["sentiment_score"]))
        
        return result
        
    except Exception as e:
        raise Exception(f"Error analyzing sentiment: {str(e)}")
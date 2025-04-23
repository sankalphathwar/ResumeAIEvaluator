# AI HR Assistant

An AI-powered HR tool with two main features:

1. **Resume Evaluator**: Compares software engineer resumes against job descriptions to provide structured feedback and match scoring
2. **Employee Sentiment Analysis**: Analyzes employee feedback to predict attrition risks and recommend retention strategies

## Features

### Resume Evaluator
- Upload resumes in multiple formats (PDF, DOCX, TXT)
- Analyze resumes against job descriptions
- Get detailed match scores, skill comparisons, and recommendations
- View previous evaluations from the database
- Download evaluation reports

### Employee Sentiment Analysis
- Analyze employee feedback (surveys, exit interviews, etc.)
- Predict attrition risks (High/Medium/Low)
- Identify key concerns and positive aspects
- Get actionable retention recommendations
- View previous sentiment analyses from the database
- Download sentiment analysis reports

## Technical Stack
- **Frontend**: Streamlit
- **Backend**: Python
- **AI**: Google Gemini API
- **Database**: PostgreSQL
- **Additional Libraries**: pandas, plotly, sqlalchemy

## Setup Instructions

1. Clone the repository:
```
git clone https://github.com/your-username/ai-hr-assistant.git
cd ai-hr-assistant
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Set up environment variables:
```
# Create a .env file with the following variables
GOOGLE_API_KEY=your_google_api_key
DATABASE_URL=postgresql://username:password@host:port/database
```

4. Run the application:
```
streamlit run app.py
```

## Database Schema

The application uses two main tables:

1. **resume_evaluations**: Stores resume evaluation results
2. **employee_sentiments**: Stores employee sentiment analysis results

## License

MIT

## Credits

Developed using Google's Gemini AI API
import os
import datetime
import json
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Get database URL from environment variables
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not found.")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)
Base = declarative_base()

# Define Resume Evaluation model
class ResumeEvaluation(Base):
    __tablename__ = 'resume_evaluations'
    
    id = Column(Integer, primary_key=True)
    resume_text = Column(Text)
    job_description = Column(Text)
    result_json = Column(Text)  # Store the full result as JSON
    overall_match_score = Column(Float)
    recommendation = Column(String(20))  # Strong/Moderate/Weak Fit
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<ResumeEvaluation(id={self.id}, score={self.overall_match_score}, recommendation='{self.recommendation}')>"
    
    @property
    def result(self):
        """Convert stored JSON back to dictionary"""
        if self.result_json:
            return json.loads(self.result_json)
        return {}

# Define Employee Sentiment model
class EmployeeSentiment(Base):
    __tablename__ = 'employee_sentiments'
    
    id = Column(Integer, primary_key=True)
    feedback_text = Column(Text)
    result_json = Column(Text)  # Store the full result as JSON
    sentiment_score = Column(Float)
    attrition_risk = Column(String(10))  # High/Medium/Low
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<EmployeeSentiment(id={self.id}, score={self.sentiment_score}, risk='{self.attrition_risk}')>"
    
    @property
    def result(self):
        """Convert stored JSON back to dictionary"""
        if self.result_json:
            return json.loads(self.result_json)
        return {}

# Create tables if they don't exist
Base.metadata.create_all(engine)

# Create a session factory
Session = sessionmaker(bind=engine)

def store_resume_evaluation(resume_text, job_description, result):
    """
    Store a resume evaluation result in the database
    
    Args:
        resume_text (str): The resume text
        job_description (str): The job description text
        result (dict): The evaluation result dictionary
        
    Returns:
        ResumeEvaluation: The stored evaluation record
    """
    try:
        session = Session()
        
        # Create a new evaluation record
        evaluation = ResumeEvaluation(
            resume_text=resume_text,
            job_description=job_description,
            result_json=json.dumps(result),
            overall_match_score=result.get('overall_match_score', 0),
            recommendation=result.get('recommendation', 'Unknown')
        )
        
        # Add and commit to database
        session.add(evaluation)
        session.commit()
        
        return evaluation
        
    except Exception as e:
        session.rollback()
        raise Exception(f"Error storing resume evaluation: {str(e)}")
    finally:
        session.close()

def get_resume_evaluations(limit=10):
    """
    Get recent resume evaluations from the database
    
    Args:
        limit (int): Maximum number of records to retrieve
        
    Returns:
        list: List of ResumeEvaluation objects
    """
    try:
        session = Session()
        evaluations = session.query(ResumeEvaluation).order_by(
            ResumeEvaluation.timestamp.desc()
        ).limit(limit).all()
        return evaluations
    except Exception as e:
        raise Exception(f"Error retrieving resume evaluations: {str(e)}")
    finally:
        session.close()

def store_sentiment_analysis(feedback_text, result):
    """
    Store a sentiment analysis result in the database
    
    Args:
        feedback_text (str): The employee feedback text
        result (dict): The sentiment analysis result dictionary
        
    Returns:
        EmployeeSentiment: The stored sentiment record
    """
    try:
        session = Session()
        
        # Create a new sentiment record
        sentiment = EmployeeSentiment(
            feedback_text=feedback_text,
            result_json=json.dumps(result),
            sentiment_score=result.get('sentiment_score', 0),
            attrition_risk=result.get('attrition_risk', 'Unknown')
        )
        
        # Add and commit to database
        session.add(sentiment)
        session.commit()
        
        return sentiment
        
    except Exception as e:
        session.rollback()
        raise Exception(f"Error storing sentiment analysis: {str(e)}")
    finally:
        session.close()

def get_sentiment_analyses(limit=10):
    """
    Get recent sentiment analyses from the database
    
    Args:
        limit (int): Maximum number of records to retrieve
        
    Returns:
        list: List of EmployeeSentiment objects
    """
    try:
        session = Session()
        sentiments = session.query(EmployeeSentiment).order_by(
            EmployeeSentiment.timestamp.desc()
        ).limit(limit).all()
        return sentiments
    except Exception as e:
        raise Exception(f"Error retrieving sentiment analyses: {str(e)}")
    finally:
        session.close()
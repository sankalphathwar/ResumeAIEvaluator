import re
import pandas as pd

def extract_skills(text):
    """
    Extract potential skills from text using a simple regex-based approach
    
    Args:
        text (str): Text to extract skills from
        
    Returns:
        list: List of potential skills
    """
    # Common programming languages
    programming_languages = [
        "Python", "Java", "JavaScript", "C\\+\\+", "C#", "Ruby", "PHP", 
        "Swift", "Kotlin", "Go", "Rust", "TypeScript", "Scala", "Perl",
        "R", "MATLAB", "SQL", "HTML", "CSS", "Bash", "Shell"
    ]
    
    # Common frameworks and libraries
    frameworks = [
        "React", "Angular", "Vue", "Django", "Flask", "Spring", "Express", 
        "Node\\.js", "TensorFlow", "PyTorch", "Keras", "Pandas", "NumPy",
        "Scikit-learn", "Laravel", "Ruby on Rails", "ASP\\.NET", ".NET"
    ]
    
    # Common tools and technologies
    tools = [
        "Git", "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Jenkins", 
        "CI/CD", "REST", "GraphQL", "Microservices", "Agile", "Scrum",
        "JIRA", "Confluence", "Linux", "Windows", "MacOS", "MongoDB",
        "PostgreSQL", "MySQL", "Oracle", "Redis", "Elasticsearch"
    ]
    
    # Combine all keywords
    keywords = programming_languages + frameworks + tools
    
    # Create a regex pattern
    pattern = r'\b(' + '|'.join(keywords) + r')\b'
    
    # Find all matches
    matches = re.findall(pattern, text, re.IGNORECASE)
    
    # Remove duplicates and sort
    skills = sorted(list(set([match.lower() for match in matches])))
    
    return skills

def create_skills_dataframe(resume_skills, job_skills):
    """
    Create a dataframe comparing skills in resume and job description
    
    Args:
        resume_skills (list): Skills extracted from resume
        job_skills (list): Skills extracted from job description
        
    Returns:
        pandas.DataFrame: DataFrame with skill matching information
    """
    # Create sets for comparison
    resume_set = set(resume_skills)
    job_set = set(job_skills)
    
    # Find matching and missing skills
    matching = list(resume_set.intersection(job_set))
    missing = list(job_set - resume_set)
    additional = list(resume_set - job_set)
    
    # Create a dataframe
    data = {
        'Matching Skills': pd.Series(matching),
        'Missing Skills': pd.Series(missing),
        'Additional Skills': pd.Series(additional)
    }
    
    return pd.DataFrame(data)

def calculate_match_percentage(resume_skills, job_skills):
    """
    Calculate the percentage match between resume skills and job skills
    
    Args:
        resume_skills (list): Skills extracted from resume
        job_skills (list): Skills extracted from job description
        
    Returns:
        float: Percentage of job skills found in resume
    """
    if not job_skills:
        return 0.0
    
    resume_set = set(resume_skills)
    job_set = set(job_skills)
    
    matches = len(resume_set.intersection(job_set))
    
    return (matches / len(job_set)) * 100

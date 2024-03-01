import spacy
import psycopg2
import pandas as pd
from psycopg2 import sql
import re
import spacy
from spacy.matcher import PhraseMatcher
from skillNer.general_params import SKILL_DB
from skillNer.skill_extractor_class import SkillExtractor
# Load the English language model
nlp = spacy.load("en_core_web_sm")


def extract_required_experience(job_description):
    # Define pattern for required experience using regular expression
    pattern = r"\b([0-9]+)\s?\+?\s?(?:years?|yrs?)\b"
    
    # Search for pattern in job description
    match = re.search(pattern, job_description, re.IGNORECASE)
    
    if match:
        required_experience = int(match.group(1))
        return required_experience
    else:
        return None

# Example usage:
job_description = """
We are seeking a highly motivated individual with extensive experience in software development. 
Responsibilities include designing and implementing new features, collaborating with cross-functional teams, 
and ensuring code quality. Requirements: Bachelor's degree in Computer Science, 5+ years of experience in 
Python development, strong problem-solving skills.
"""

required_experience = extract_required_experience(job_description)
if required_experience is not None:
    print("Required experience:", required_experience, "years")
else:
    print("No required experience found in the job description.")

def extract_job_role(job_description):
    # Process the job description text
    doc = nlp(job_description)
    #df = getNewSkills()
    # Define keywords related to job roles
    #job_role_keywords = ["role", "responsibilities", "duties", "position", "job title", "experience", "skills", "location", "tecnologies", "soft skills"]
    job_role_keywords = [" ", ",",  " , "]
    
    # Initialize an empty list to store extracted job roles
    job_roles = []
    
    # Iterate through the sentences in the document
    for sent in doc.sents:
        # Check if any of the job role keywords are present in the sentence
        if any(keyword in sent.text.lower() for keyword in job_role_keywords):
            # Extract noun phrases that represent job roles
            for chunk in sent.noun_chunks:
                
                job_roles.append(chunk.text)
                               
    # Return the extracted job roles
    return job_roles

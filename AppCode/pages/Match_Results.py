import streamlit as st
import psycopg2
from psycopg2 import sql
import pandas as pd
import requests
import re
from WebAPI import WebAPIURL
db_params = {
    'host': 'dpg-cnhir5fsc6pc73dvj380-a.oregon-postgres.render.com',
    'database': 'OpenAI',
    'user': 'anu',
    'password': '5omRLogf9Kdas3zoBFPCT9yrCGU4IbEX',
}
st.header("Profile - Job Description Match Results")
 
def ShowResults():
   api_url = WebAPIURL.GetWebAPIURL('AllProfileMatchResults')
   response = requests.get(api_url)
   df =(response.json())
   st.dataframe(df,use_container_width = True, hide_index = True) 

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
def allCVExp():
    dbQuery = "select * from coursemaster"
    conn = psycopg2.connect(**db_params)   
    df = pd.read_sql_query(dbQuery, conn)
    for index, row in df.iterrows():
        id_value = row['masterid']
        desc = row['description']
        exxp = extract_required_experience(desc)
        if(exxp != 'None'):
            print("Profile Experience " + str(exxp) + " for id - " + str(id_value))
def allJDExp():
    dbQuery = "select * from jdmaster"
    conn = psycopg2.connect(**db_params)   
    df = pd.read_sql_query(dbQuery, conn)
    for index, row in df.iterrows():
        id_value = row['jdmasterid']
        desc = row['jobdescription']
        exxp = extract_required_experience(desc)
        if(exxp != 'None'):
            print("Job Experience " + str(exxp) + " for id - " + str(id_value))            
            
ShowResults()
allCVExp()
allJDExp()
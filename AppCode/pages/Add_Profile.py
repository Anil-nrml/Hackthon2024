import streamlit as st
from PyPDF2 import PdfReader
import os
import psycopg2
from psycopg2 import sql
import pandas as pd
from datetime import date
import numpy as np
import time
import spacy
import numpy
from sentence_transformers import SentenceTransformer, util
from io import StringIO 
from spacy.matcher import PhraseMatcher
from skillNer.general_params import SKILL_DB
from skillNer.skill_extractor_class import SkillExtractor
from datetime import datetime
from psycopg2.extensions import register_adapter, AsIs
register_adapter(np.int64, AsIs)
import warnings
warnings.filterwarnings('ignore')
def addapt_numpy_float64(numpy_float64):
    return AsIs(numpy_float64)
def addapt_numpy_int64(numpy_int64):
    return AsIs(numpy_int64)
register_adapter(numpy.float64, addapt_numpy_float64)
register_adapter(numpy.int64, addapt_numpy_int64)

db_params = {
    'host': 'dpg-cnhir5fsc6pc73dvj380-a.oregon-postgres.render.com',
    'database': 'OpenAI',
    'user': 'anu',
    'password': '5omRLogf9Kdas3zoBFPCT9yrCGU4IbEX',
}
nlp = spacy.load("en_core_web_lg")
    # init skill extractor
skill_extractor = SkillExtractor(nlp, SKILL_DB, PhraseMatcher)
count = 0
filePath = "Vaibhav"
source = "JD"
def tuple_to_int(tup):
    if len(tup) == 1:
        return tup[0]
    else:
        return tup[0] * (10 ** (len(tup) - 1)) + tuple_to_int(tup[1:])
def SkillExtract():

    # Connect to the PostgreSQL database
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()


    # Retrieve "id" and "description" columns from the table
    #query = sql.SQL("select jdmasterid,jobdescription from JDMaster where isskillsextracted in (0)")
    query = "select masterid,description,filename from CourseMaster where isskillsextracted in (0)"

    # Use Pandas to read the data into a DataFrame
    df = pd.read_sql_query(query, conn)

    # Print the DataFrame (for demonstration purposes)
    #print(df)
    
    skill_details = 'Programming'
    skill_type = 'Technical'
    weightage = -1.0
    is_active = True
    Skillid = 1
    jdMasterid = 1
    OldSkillCount = 0
    NewSkillCount = 0
    if(len(df.index) > 0):
        print("Total Profiles for Extractraction : " + str(len(df.index)))
    for index, row in df.iterrows():
        # Access individual columns using column names
        id_value = row['masterid']
        filename_jd = row['filename']
        OldSkillCount = 0
        NewSkillCount = 0
        skill_score = 0.0
        print("Extracting Skills For ", filename_jd + " , Id : " + str(id_value) + " , Index " + str(index + 1))

        description_value = row['description']
        #print(description_value)
        
        annotations = skill_extractor.annotate(description_value)
        matches = annotations['results']['full_matches']+annotations['results']['ngram_scored']
        skills_list = []
        for result in matches:
            if(1==1):
                
                isOld = "Yes"
                skill_id = result['skill_id']
                skill_name1 = skill_extractor.skills_db[skill_id]['skill_name']
                skill_name = skill_name1.split("(")[0].strip()
                skill_type = skill_extractor.skills_db[skill_id]['skill_type']
                skill_score = round(result['score'],2)
                

                if( skill_name in skills_list):
                    continue
                skills_list.append(skill_name)
                #print("Skill Identified : ", j['doc_node_value'])
                query = "SELECT skillid FROM skillmaster WHERE upper(skillDetails) IN (%s)"
                params = (skill_name.upper(),)  # Replace 'Test' with your actual variable or user input
                cursor.execute(query, params)
                if cursor.rowcount > 0:    
                    print("Skill Identified : ", skill_name)                
                    result = cursor.fetchall()   
                    #print(result)             
                    for row in result:
                        row_as_int = [int(element) for element in row]
                        #print(id_value)
                        #print(row_as_int[0])
                        OldSkillCount = OldSkillCount + 1
                        isOld = "Yes"
                        query = "SELECT skillid FROM CourseSkilldetails WHERE skillid IN (%s) and Masterid in (%s)"
                        params = (row_as_int[0],id_value,)  
                        cursor.execute(query, params)
                        if cursor.rowcount > 0: 
                            weightage = -1.0  
                            #print("Skill Already in SkillMaster and JDSkillDetails")
                        else:  
                            
                            
                            query = "Select max(skilldetailsid) from courseskilldetails"                
                            df = pd.read_sql_query(query, conn)
                            CourseID = df.iat[0,0] + 1

                            Skillid = row_as_int[0]
                            jdMasterid = id_value   
                            insert_query = sql.SQL("""INSERT INTO Courseskilldetails (skilldetailsid, Skillid, Masterid) VALUES (%s, %s, %s)""")
                            cursor.execute(insert_query, (CourseID, Skillid, jdMasterid))
                            conn.commit()
                            #print("Skill Already in SkillMaster and Inserted in JDSkillDetails")	
                            #print(row_as_int)
                else:    
                    NewSkillCount = NewSkillCount + 1
                    isOld = "No"
                    skill_details = skill_name              
                    weightage = -1.0
                    skill_score = skill_score * 100               
                    skill_score1 = str(skill_score)
                    #skill_score = skill_score.astype(float)   
                    #print(skill_score)         
                    insert_query = sql.SQL("""INSERT INTO SkillMaster (SkillDetails, SkillType, Weightage, IsActive, skill_score) 
                    VALUES (%s, %s, %s, %s, %s) RETURNING SkillID""")
                    cursor.execute(insert_query, (skill_details, skill_type, weightage, is_active, skill_score1))
                    conn.commit()
                    generated_skill_id = cursor.fetchone()[0]
                    Skillid = generated_skill_id
                    jdMasterid = id_value

                    query = "Select max(skilldetailsid) from courseskilldetails"                
                    df = pd.read_sql_query(query, conn)
                    CourseID = df.iat[0,0] + 1

                    insert_query = sql.SQL("""INSERT INTO CourseSkilldetails (skilldetailsid,Skillid, Masterid) VALUES (%s, %s, %s)""")
                    cursor.execute(insert_query, (CourseID,Skillid, jdMasterid))
                    conn.commit()
                    print("Skill Identified : ", skill_name)
                    #print("Skill inserted in SkillMaster and Inserted in JDSkillDetails")

        query = "update public.coursemaster set isskillsextracted = 1 where masterid = (%s)"
        
        params = (id_value,)  
        cursor.execute(query, params)
        conn.commit()
        print("Skills Updated for Skills Extraction for file ", filename_jd)
        print("Total Skills : ", len(skills_list))
        
        
    # Close the cursor and connection
    cursor.close()
    # Close the connection
    conn.close()
def FileUpload(text, filePath):   

    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()    
    query = "Select case when max(masterid) is null then 1 else max(masterid) end as masterid from courseMaster"                
    df = pd.read_sql_query(query, conn)
    if(df.iat[0,0] == 0):
        MasterId = 1
    else:
        MasterId = df.iat[0,0] + 1
    #MasterId=1
    #print(MasterId)
    query =sql.SQL("""INSERT INTO  CourseMaster (masterid,description, filename, UploadedDate, IsDetailsExtracted,IsSkillsExtracted,source) VALUES (%s,%s,%s,%s,%s,%s,%s)""")
    cursor.execute(query, (MasterId,text,filePath, date.today(),0,0,source)) 
    
    conn.commit()

    cursor.close()
    conn.close()

    print(filePath , " File Upload Done")
def AllSkillMatch():
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    query = "select jdmasterid from jdmaster where isskillsextracted in (1)"

    # Use Pandas to read the data into a DataFrame
    df = pd.read_sql_query(query, conn)
    for index, row in df.iterrows():
        # Access individual columns using column names
        id_value = row['jdmasterid']        
        SkillMatcher(id_value)

def SkillMatcher(JDId):
  print("Checking Best Profile for the JD...")  
  conn = psycopg2.connect(**db_params)
  cursor_obj = conn.cursor()

  query = "select * from alljdskills where jdmasterid = "+ str(JDId)
  cursor_obj.execute(query)
  jd_data = cursor_obj.fetchall()
  #connection_obj.commit()
  print(jd_data)
  query = "select * from CourseDetailsForMatching"
  cursor_obj.execute(query)
  cv_data = cursor_obj.fetchall()
  print(cv_data)
  #connection_obj.commit()
  query = "select jdmasterid || '-' || courseid from courseskillmatch"
  cursor_obj.execute(query)
  match_data = cursor_obj.fetchall()

  jd_skills = {}
  for obj in jd_data:
    if obj[0] not in jd_skills:
      jd_skills[obj[0]] = []

    jd_skills[obj[0]].append(obj[1])

  cv_skills = {}
  for obj in cv_data:
    if obj[0] not in cv_skills:
      cv_skills[obj[0]] = []
    
    cv_skills[obj[0]].append(obj[1])

  model = SentenceTransformer('all-MiniLM-L6-v2')
  count = 0
  MatchSkillsId = 0
  isAlreadyInDb = False
  TopScore = 0
  CourseId = 0
  for jd in jd_skills:
    for cv in cv_skills:
      #if(cv in match_data[1] and jd in match_data[0]):
      #print("Already record : " + str(cv) + " , "  + str(jd))
      isAlreadyInDb = False
      match_details = str(jd) + "-" + str(cv)
      print("Checking for existing Profile")
      for i in match_data:
        if(i[0] == match_details):
          print( "Already in Database -----------"  + i[0])
          isAlreadyInDb = True
          break
      
      if(isAlreadyInDb == True):
        continue
      #print(match_details)  
      print("Running Matching Algo")
      count += 1
      sentence1 = " ".join(cv_skills[cv])
      sentence2 = " ".join(jd_skills[jd])
      embedding1 = model.encode(sentence1, convert_to_tensor=True)
      embedding2 = model.encode(sentence2, convert_to_tensor=True)

      # Compute cosine similarity between the two sentence embeddings
      cosine_similarit = util.cos_sim(embedding1, embedding2)
      if(TopScore < cosine_similarit * 100):
        TopScore = cosine_similarit * 100
        CourseId = cv
      
      print("DB Entry for Matching Results")  
      #common = set(cv_skills[cv]) & set(jd_skills[jd])
      if(1==1):
        if(MatchSkillsId == 0):
            query = "select coalesce(max(skillmatchid),0) + 1 from courseskillmatch"
            cursor_obj.execute(query)
            MatchId = cursor_obj.fetchall()
            MatchSkillsId = tuple_to_int( MatchId[0])
      

      
      if(1==1):  
        record = (MatchSkillsId, cv, jd, cosine_similarit[0][0].item(),1)
        query = """INSERT INTO public.courseskillmatch(SkillMatchID, courseid, JDMasterID, MatchScore,isactive) VALUES (%s,%s,%s,%s,%s)"""
        cursor_obj.execute(query, record)
        conn.commit()
        MatchSkillsId = MatchSkillsId + 1
      print( str( MatchSkillsId)  + " "+"Updating in DB - JD {} CV {} ".format(jd, cv), cosine_similarit[0][0].item())
    #print(TopScore)

    
  cursor_obj.close()
  conn.close()  
def submit (uploaded_resume):
    text = ""
    fName = ""
    
    if uploaded_resume:
        
        fName = uploaded_resume.name
        if fName.endswith("pdf"):
            pdf_reader = PdfReader(uploaded_resume)
            
            for page in pdf_reader.pages:
                text += page.extract_text()
            #text = extract_text(filePath)
       
        elif fName.endswith("doc") or fName.endswith("docx"):
            text = StringIO(uploaded_resume.getvalue().decode("utf-8"))
            text = text.read()
    
        else:
            text = uploaded_resume.getvalue().decode()
         #Pdf Text Extraction
        with st.spinner('Processing...'):
            FileUpload(text,fName)
            st.success('File uploaded successfully')
            SkillExtract()
            st.success('Skills extracted from file')
            #AllSkillMatch()
            #st.success('Skills match results updated')
    
    else:
        AllSkillMatch()            
           


def main():
    st.header("Best Resume Matching Engine")

    form = st.form(key='some_form')
    uploaded_resume = form.file_uploader("Upload Profile Description" , type = ["txt","pdf"])    
    form.form_submit_button("Run", on_click=submit(uploaded_resume=uploaded_resume))

if __name__ == '__main__':
    main()


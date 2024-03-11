import streamlit as st
import socket
from PyPDF2 import PdfReader
import psycopg2
from psycopg2 import sql
import pandas as pd
from datetime import date
import numpy as np
import spacy
import re
from sentence_transformers import SentenceTransformer, util
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from io import StringIO 
from spacy.matcher import PhraseMatcher
from skillNer.general_params import SKILL_DB
from skillNer.skill_extractor_class import SkillExtractor
from psycopg2.extensions import register_adapter, AsIs
register_adapter(np.int64, AsIs)
import warnings
warnings.filterwarnings('ignore')
st.set_page_config(
    page_title="Home",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded" 
)
model = SentenceTransformer('all-MiniLM-L6-v2')
#db_params = {     'host': 'dpg-clur07la73kc73bjt21g-a.oregon-postgres.render.com',    'database': 'anudip',    'user': 'anu',    'password': 'GdMdskphcmhZZblHM30cPw75gl4l8oxJ',}
db_params = {
    'host': 'dpg-cnhir5fsc6pc73dvj380-a.oregon-postgres.render.com',
    'database': 'OpenAI',
    'user': 'anu',
    'password': '5omRLogf9Kdas3zoBFPCT9yrCGU4IbEX',
}
nlp = spacy.load("en_core_web_lg")
    # init skill extractor
skill_extractor = SkillExtractor(nlp, SKILL_DB, PhraseMatcher)

with st.sidebar:
    st.title("Best Resume Fit Matching Engine")
    st.markdown('''
    ## About
    Goal is to match the input profile with Job Descriptions and rank them with best match score
    ''')

def tuple_to_int(tup):
    if len(tup) == 1:
        return tup[0]
    else:
        return tup[0] * (10 ** (len(tup) - 1)) + tuple_to_int(tup[1:])

def skill_check(dbQuery):
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    df = pd.read_sql_query(dbQuery, conn)
    Required_Skills=''
    for index, row in df.iterrows():   
    
        skillname = row['skillname']
        Required_Skills = Required_Skills + ', '+ skillname
    
    Required_Skills = Required_Skills[2:] 
    return Required_Skills
def display_skills(id):
    jd=str(id)
    query = "select skillname from SkillDetails  where id = "+ jd +" and skillscore > 99 and skilltype = 'Hard Skill'"
    RequiredSkills_Hard  = skill_check(query)

    query = "select skillname from SkillDetails  where id = "+ jd +" and skillscore > 50 and skilltype = 'Soft Skill'"  
    RequiredSkills_Soft  = skill_check(query)

    query = "select skillname from SkillDetails  where id = "+ jd +" and skillscore < 50 and skilltype = 'Soft Skill'"  
    RequiredSkills_G1  = skill_check(query)

    query = "select skillname from SkillDetails  where id = "+ jd +" and skillscore < 99 and skilltype = 'Hard Skill'"  
    RequiredSkills_G2  = skill_check(query)

    print('')
    print("Required Skills      : " + RequiredSkills_Hard)
    print('')
    print("Required Soft Skills : " + RequiredSkills_Soft)
    print('')
    print("Good to have Skills  : " + RequiredSkills_G1 +  " " + RequiredSkills_G2)
    return RequiredSkills_Hard + "@" + RequiredSkills_Soft + "@" + RequiredSkills_G1 + "@" + RequiredSkills_G2

def latestSkillDetails(jid):
    query = "select * from jdmaster where isskillsextracted=1 order by jdmasterid desc limit 1 "
    conn = psycopg2.connect(**db_params)
    df = pd.read_sql_query(query, conn)
    filename = df.iat[0,2]
    fileId = df.iat[0,0]
    
    upload = df.iat[0,3]
    if(fileId != jid):
        print("Skill Details for File : " + str(filename) + " , ID " + str(fileId) + " , Uploaded on " + str(upload))
        data = display_skills(fileId)
        jid = df.iat[0,0]
    return data

def SkillExtract():
    print("Extracting Skills for the JD...")
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()


    # Retrieve "id" and "description" columns from the table
    #query = sql.SQL("select jdmasterid,jobdescription from JDMaster where isskillsextracted in (0)")
    query = "select jdmasterid,jobdescription,filename from JDMaster where isskillsextracted in (0)"

    # Use Pandas to read the data into a DataFrame
    df = pd.read_sql_query(query, conn)

    # Print the DataFrame (for demonstration purposes)
    #print(df)
    
    skill_details = ''
    skill_type = ''
    weightage = -1.0
    is_active = True
    Skillid = 0
    jdMasterid = 0
    OldSkillCount = 0
    NewSkillCount = 0
    if(len(df.index) > 0):
        print("Total JDs for Extractraction : " + str(len(df.index)))
    for index, row in df.iterrows():
        # Access individual columns using column names
        id_value = row['jdmasterid']
        filename_jd = row['filename']
        OldSkillCount = 0
        NewSkillCount = 0
        skill_score = 0.0
        print("Extracting Skills For ", filename_jd + " , Id : " + str(id_value) + " , Index " + str(index + 1))

        description_value = row['jobdescription']
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
                query = "SELECT skillid FROM skillmaster WHERE skillDetails IN (%s)"
                params = (skill_name,)  # Replace 'Test' with your actual variable or user input
                cursor.execute(query, params)
                if cursor.rowcount > 0:    
                    print("Skill Identified : ", skill_name)                
                    result = cursor.fetchall()                
                    for row in result:
                        row_as_int = [int(element) for element in row]
                        #print("Skill Already in SkillMaster")
                        OldSkillCount = OldSkillCount + 1
                        isOld = "Yes"
                        query = "SELECT skillid FROM jdSkilldetails WHERE skillid IN (%s) and jdMasterid in (%s)"
                        params = (row_as_int[0],id_value,)  
                        cursor.execute(query, params)
                        if cursor.rowcount > 0: 
                            weightage = -1.0  
                            #print("Skill Already in SkillMaster and JDSkillDetails")
                        else:  
                            Skillid = row_as_int[0]
                            jdMasterid = id_value   
                            insert_query = sql.SQL("""INSERT INTO jdSkilldetails (Skillid, jdMasterid) VALUES (%s, %s)""")
                            cursor.execute(insert_query, (Skillid, jdMasterid))
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
                    insert_query = sql.SQL("""INSERT INTO jdSkilldetails (Skillid, jdMasterid) VALUES (%s, %s)""")
                    cursor.execute(insert_query, (Skillid, jdMasterid))
                    conn.commit()
                    print("Skill Identified : ", skill_name)
                    #print("Skill inserted in SkillMaster and Inserted in JDSkillDetails")
        extractWords(description_value,id_value)
        query = "update public.jdmaster set isskillsextracted = 1 where jdmasterid = (%s)"
        
        params = (id_value,)  
        cursor.execute(query, params)
        conn.commit()
        print("Skills Updated for Skills Extraction for file ", filename_jd)
        print("Total Skills : ", len(skills_list))

def GetSkillId(skillname,jdmasterid):    
    #Fetching skill id from skillmaster
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    query = "select skillid from skillmaster where upper(skilldetails) = (%s)"
    params = (skillname.upper(),)  
    cursor.execute(query, params)
    generated_skill_id = cursor.fetchone()[0]
    #jdmasterid = 912
    #print(generated_skill_id)
    #checking if skill id already in skilldetails
    query = "SELECT skillid FROM jdSkilldetails WHERE skillid IN (%s) and jdMasterid in (%s)"
    params = (generated_skill_id,jdmasterid,)  
    cursor.execute(query, params)
    if cursor.rowcount > 0: 
        #print("Already")
        query =''
    else:
        #print("Updating in DB")
        insert_query = sql.SQL("""INSERT INTO jdSkilldetails (Skillid, jdMasterid) VALUES (%s, %s)""")
        cursor.execute(insert_query, (generated_skill_id, jdmasterid))
        conn.commit()

    cursor.close()
    # Close the connection
    conn.close()   
    return generated_skill_id

def getNewSkills():
    query = "select skillid,skilldetails,skilltype,skill_score from skillmaster where weightage = -2"
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    df_skill_master = pd.read_sql_query(query, conn)
    df_skill_master['skilldetails'] = df_skill_master['skilldetails'].str.upper()
    cursor.close()
    # Close the connection
    conn.close()

    #print(df_skill_master)
    return df_skill_master
def skill_Validate(df, skill):
    skill = skill.upper()
    if (len(skill.split()) < 2 and len(skill) < 3) or len(skill.split())==1:
        df['skill_present'] = df['skilldetails'].apply(lambda x: re.match(rf'^{skill}$', x))
        if any(df['skill_present']):
            #print("Valid Skill")
            return 1
        else:
            #print("Not a Skill")
            return 0
    elif df['skilldetails'].str.contains(skill.upper()).any():
        #print("Valid Skill")
        return 1
    else:
        # print("Not a Skill")
        return 0 
def extractWords(job_description,JdMasterid):
    job_roles = []
    job_description = job_description.replace(')',' ')
    delimiters = ",", " ", " , ", ";","\n","/","\\"
    regex_pattern = '|'.join(map(re.escape, delimiters))
    df = getNewSkills()
    data = re.split(regex_pattern, job_description)
    #data = job_description.split(',')
    for ds in data:
        #print(ds)
        try:
            if(skill_Validate(df,ds.strip())):                
                job_roles.append(ds) 
                GetSkillId(ds.strip(),JdMasterid)
                print("Skills Identified* : " + ds)   
        except Exception as error:
            test = 1
    return job_roles  

def extract_job_role(job_description):
    # Process the job description text
    doc = nlp(job_description)
    df = getNewSkills()
    # Define keywords related to job roles
    job_role_keywords = ["role", "responsibilities", "duties", "position", "job title", "experience", "skills", "location", "tecnologies", "soft skills"]
    #job_role_keywords = ["location"]
    
    # Initialize an empty list to store extracted job roles
    job_roles = []
    
    # Iterate through the sentences in the document
    for sent in doc.sents:
        # Check if any of the job role keywords are present in the sentence
        if any(keyword in sent.text.lower() for keyword in job_role_keywords):
            # Extract noun phrases that represent job roles
            for chunk in sent.noun_chunks:
                print("NLP-" + chunk.text)
                if(skill_Validate(df,chunk.text)):
                    job_roles.append(chunk.text)
                    print("Skills Identified* : " + chunk.text)
                
    # Return the extracted job roles
    return job_roles
        
def SkillExtraction(file):
    annotations = skill_extractor.annotate(file)

    matches = annotations['results']['full_matches']+annotations['results']['ngram_scored']

    skills_dict = {}
    for result in matches:
        skill_id = result['skill_id']
        skill_name = skill_extractor.skills_db[skill_id]['skill_name']
        skill_type = skill_extractor.skills_db[skill_id]['skill_type']
        skill_score = round(result['score'],2)
        st.write("Skills----------")   
        st.write(skill_name)    
        st.write(skill_type)   
        st.write(skill_score)            
        st.write("Skills----------")   

def SkillMatcher(model):
  print("Checking Best Course for the JD...")  
  conn = psycopg2.connect(**db_params)
  cursor_obj = conn.cursor()

  query = "select * from JDDetailsCoursematching"
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
    print(CourseId)
    query = "select filename from coursemaster where masterid = " + str(CourseId)
    df = pd.read_sql_query(query, conn)
    try:
        MatchId = df.iat[0,0].split('.')[0]
    except:
        print(CourseId)    
    print("------------------------Beta Results for Course - " + MatchId)
    return MatchId
  cursor_obj.close()
  conn.close()  
       
def LatestExtractedSkills():
   dbQuery = "select * from LatestSkills"
   conn = psycopg2.connect(**db_params)   
   df = pd.read_sql_query(dbQuery, conn)
   st.dataframe(df,use_container_width = True, hide_index = True)
def Last20JD():
   dbQuery = "select * from TopJD"
   conn = psycopg2.connect(**db_params)   
   df = pd.read_sql_query(dbQuery, conn)
   st.dataframe(df,use_container_width = True, hide_index = True)  
def ProfileMatchResults(Jobid):
   conn = psycopg2.connect(**db_params)  
   dbQuery = "select * from ProfileMatch where jobid = " + str(Jobid)         
   df = pd.read_sql_query(dbQuery, conn)
   st.dataframe(df,use_container_width = True, hide_index = True)         
def Executequery(dbquery):
    conn = psycopg2.connect(**db_params)
    cursor_obj = conn.cursor()    
    cursor_obj.execute(dbquery)
    cursor_obj.close()
    conn.close() 
def uploadFile(text,filePath):
    hostname = socket.gethostname()
## getting the IP address using socket.gethostbyname() method
    ip_address = socket.gethostbyname(hostname)
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()    
    query = "Select max(jdmasterid) from JdMaster"                
    df = pd.read_sql_query(query, conn)
    try:
        MasterId = df.iat[0,0] + 1
    except:
        MasterId =1
    uploadedBy = hostname + ip_address
    #print(MasterId)
    query =sql.SQL("""INSERT INTO  JDMaster (jdmasterid,jobdescription, filename, UploadedDate, IsDetailsExtracted,IsSkillsExtracted,source,uploadedby) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""")
    cursor.execute(query, (MasterId,text,filePath, date.today(),0,0,"JD", uploadedBy)) 
    conn.commit()
    print(hostname)
    print(ip_address)
    print("File Uploaded...")
    return MasterId
def RemoveSkills(data):
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()  
    skill_rm = data.split(':')[1]
    print("Removing Skills " +  skill_rm)
    query = "update skillmaster set weightage = 0 where skilldetails = (%s)"        
    params = (skill_rm,)  
    cursor.execute(query, params)
    conn.commit()
    cursor.close()
    conn.close() 
def insert_skill(skills):
    details = skills.split(',')
    skill_details = details[0]
    skill_type = details [1]
    skill_score1 = details[2]
    weightage = -2
    is_active = True
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    print("Adding Skill " + skill_details)
    query = "SELECT skillid FROM skillmaster WHERE skillDetails IN (%s)"
    params = (skill_details,)  # Replace 'Test' with your actual variable or user input
    cursor.execute(query, params)
    if cursor.rowcount == 0:    

        insert_query = sql.SQL("""INSERT INTO SkillMaster (SkillDetails, SkillType, Weightage, IsActive, skill_score) 
                    VALUES (%s, %s, %s, %s, %s) RETURNING SkillID""")
        cursor.execute(insert_query, (skill_details, skill_type, weightage, is_active, skill_score1))
        conn.commit()
    else:
        print("Skill Already in DB")    
     # Close the cursor and connection
    cursor.close()
    # Close the connection
    conn.close()
def AddSkills(data):
    skill_add = data.split(':')[1]
    insert_skill(skill_add)    
def AppFlow(text,fName,query, IsUpload):
   profile=""
   if(len(query) > 8):
        profile = query[0:7] 
        print(profile)
   if("@Remove" in profile):
        
        RemoveSkills(query)
        st.success('Skills removed')
        return
   elif("@Add" in profile):
        AddSkills(query) 
        st.success('Skills added')
        return        
   if(IsUpload == False and len(query) > 10):
        text = query
        IsUpload = True
        query = ''
        fName = 'Open Text'
   elif(IsUpload == False and len(query) > 10):
        text = query
        IsUpload = True
        query = ''
        fName = 'Open Text'
   with st.spinner('Processing...'):
        if(query.upper() == 'SKILLS'):
            LatestExtractedSkills()
            st.success('Skills extracted from recent JDs')
        elif(query.upper() == 'JD'):            
            Last20JD()
            st.success('Recently uploaded JDs')
        elif(query.upper() == 'JD'):            
            Last20JD()
            st.success('Recently uploaded JDs')
        else:     
            if(IsUpload and query == ''):                
                Jobid = uploadFile(str(text),fName)
                SkillExtract()
                profile = SkillMatcher(model)
                ProfileMatchResults(Jobid)
                #details = latestSkillDetails(0).split('@')
                
                #st.subheader('Required Skills : ', divider='rainbow')
                #st.write(details[0])
                #st.subheader('Required Soft Skills : ', divider='rainbow')
                #st.write(details[1])
                #st.subheader('Good to have Skills : ', divider='rainbow')
                #st.write(details[2] +  " " + details[3])

                st.success('Profile Match - ' + profile)
def extract_Newjob_role(job_description):
    # Process the job description text
    doc = nlp(job_description)
    
    # Define keywords related to job roles
    job_role_keywords = ["role", "responsibilities", "duties", "position", "job title"]
    
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
def submit (uploaded_resume, query):
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
    
        AppFlow(text,fName,query, True)
    else:
        AppFlow(text,fName,query, False) 
           


def main():
    st.header("Best Resume Matching Engine")

    form = st.form(key='some_form')
    uploaded_resume = form.file_uploader("Upload Job Description" , type = ["txt","pdf"])
    query = form.text_area(
                "Skills Extraction",
                placeholder="Skills?",
                key="question"
            )
    form.form_submit_button("Run", on_click=submit(uploaded_resume=uploaded_resume, query=query))

if __name__ == '__main__':
    main()

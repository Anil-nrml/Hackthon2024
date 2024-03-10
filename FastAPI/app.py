#Fast APi Packages
from fastapi import FastAPI,File
from pydantic import BaseModel
import json

#SkillExtraction Packages
import psycopg2
import pandas as pd
import numpy as np
import spacy
from sklearn.metrics.pairwise import cosine_similarity
from spacy.matcher import PhraseMatcher
from skillNer.general_params import SKILL_DB
from skillNer.skill_extractor_class import SkillExtractor
from psycopg2.extensions import register_adapter, AsIs
register_adapter(np.int64, AsIs)
import warnings
warnings.filterwarnings('ignore')


#Custom Classes for endpoints
from DbConnection import DbConnection
from UploadFile import UploadOpenFile
from SkillExtract import SkillExtractorDetails
from ExtractContentsFromFile import ExtractContentFromFile
from RemoveSkills import RemoveSkill
import os
os.environ['HF_HOME'] = '/hug/cache/'

app = FastAPI()
class FileDetails(BaseModel):
    filecontents: str
    filename: str
    fileid: str
    message: str


class SkillDetails(BaseModel):
    skillid: int 
    requiredSkills: str
    softSkills: str
    goodToHaveSkills: str  

class SkillData(BaseModel):
    filename: str 
         
nlp = spacy.load("en_core_web_lg")
    # init skill extractor
skill_extractor = SkillExtractor(nlp, SKILL_DB, PhraseMatcher)

@app.get("/")
async def root():
 return {"SkillAPI":"SkillAPi Version 0.05"}

db_params = DbConnection.GetDbConnection()
def parse_csv(df):
    res = df.to_json(orient="records")
    parsed = json.loads(res)
    return parsed


@app.post("/UploadJobDescription/")
def uploadJobDescription(file: bytes =  File(...), FileName: str = "sample.pdf"):   
    text= ExtractContentFromFile.ExtractDataFromFile(FileName,file)
    returnID = UploadOpenFile.uploadFile(text,FileName,db_params)
    returnSkills = SkillExtractorDetails.SkillExtract(db_params,skill_extractor,returnID)     
    details = returnSkills.split('@')
    data = {'Data':['Required Skills', 'Soft Skills', 'Good to have Skills'], 'Values':[details[0], details[1], details[2]]}
    df = pd.DataFrame(data)
    return parse_csv(df) 

@app.get("/AllProfileMatchResults") 
def AllProfileMatchResults():
   dbQuery = "select * from profilematch"
   conn = psycopg2.connect(**db_params)   
   df = pd.read_sql_query(dbQuery, conn)
   return parse_csv(df) 

@app.post("/UploadOpenText/")
def UploadOpenText(file_data: FileDetails):   
   
   returnID = UploadOpenFile.uploadFile(file_data.filecontents,file_data.filename,db_params)
   file_data.filecontents = ""
   file_data.fileid = str(returnID)
   file_data.message = "File Uploaded Successfully!"
   
   return file_data


@app.post("/ExtractSkillsByJobID/")
def ExtractSkillsByJobID(skill_data: SkillDetails):
   returnSkills = SkillExtractorDetails.SkillExtract(db_params,skill_extractor,skill_data.skillid)     
   details = returnSkills.split('@')
   skill_data.requiredSkills = details[0]
   skill_data.softSkills = details[1]
   skill_data.goodToHaveSkills = details[1]
   return skill_data

@app.post("/RemoveSkillsByName/")
def RemoveSkills(SkillName : str):    
    RemoveSkill.RemoveSkillDetails(db_params,SkillName)
    return "Skill Removed Successfully"
#return JSONResponse(content={"message": "Here's your interdimensional portal." , "mes1":"data2"})

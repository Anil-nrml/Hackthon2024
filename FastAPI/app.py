#Fast APi Packages
from fastapi import FastAPI,File
from pydantic import BaseModel
import json

#SkillExtraction Packages

import numpy as np
from sentence_transformers import SentenceTransformer
import spacy
from spacy.matcher import PhraseMatcher
from skillNer.general_params import SKILL_DB
from skillNer.skill_extractor_class import SkillExtractor
from psycopg2.extensions import register_adapter, AsIs
register_adapter(np.int64, AsIs)
import warnings
warnings.filterwarnings('ignore')


#Custom Classes for endpoints

from SkillExtract import SkillExtractorDetails


from SkillMatcher import SkillMatch
from OpenAIResponse import OpenAIText
from DataReader import GCSBlobReader
import os
os.environ['HF_HOME'] = '/hug/cache/'

app = FastAPI()
         
nlp = spacy.load("en_core_web_lg")
    # init skill extractor
skill_extractor = SkillExtractor(nlp, SKILL_DB, PhraseMatcher)
model = SentenceTransformer('all-MiniLM-L6-v2')

@app.get("/")
async def root():
 return {"SkillAPI":"SkillAPi Version 0.05"}

def parse_csv(df):
    res = df.to_json(orient="records")
    parsed = json.loads(res)
    return parsed

@app.get("/GetMatchScore/")
def GetMatchScore(inputText : str , matchCV : int, ScanFiles : int, WithOpenAI : bool) :   
   returnSkills = SkillExtractorDetails.GetSkillData(skill_extractor,inputText)
   exp = SkillExtractorDetails.extract_required_experience(inputText)
   gcsReaderObj = GCSBlobReader()    
   myDictCV = {} 
   listOfContent = gcsReaderObj.read_all_files_from_gcs('hackathon1415',ScanFiles)
   for count in range(ScanFiles):
        if(WithOpenAI):        
            airesponse = OpenAIText.OpenAITextResponse('Summarize data for skills in max 50 words',listOfContent[count]['content'])
            returnSkillsCV = SkillExtractorDetails.GetSkillData(skill_extractor,airesponse) 
        else:
            airesponse = listOfContent[count]['content']     
            returnSkillsCV = SkillExtractorDetails.GetSkillData(skill_extractor,airesponse) 
         
        myDictCV[listOfContent[count]['name']] = returnSkillsCV

   myDictJD = {} 
   myDictJD["JD1"] = returnSkills
   
   
   data = SkillMatch.SkillMatchResult(model,myDictJD,myDictCV)
   print(airesponse)
   #print(exp)
   return data

@app.get("/GetMatchScoreTest/")
def GetMatchScoreTest(inputText : str , matchCV : int, ScanFiles : int, WithOpenAI : bool) :   
   returnSkills = SkillExtractorDetails.GetSkillData(skill_extractor,inputText)
   exp = SkillExtractorDetails.extract_required_experience(inputText)
   gcsReaderObj = GCSBlobReader()    
   myDictCV = {} 
   listOfContent = gcsReaderObj.read_all_files_from_gcs('hackathon1415',ScanFiles)
   for count in range(ScanFiles):
        if(WithOpenAI):   
            expCV = SkillExtractorDetails.extract_required_experience(listOfContent[count]['content'])   
            print(listOfContent[count]['name']) 
            print(expCV) 
            if(exp  == expCV):
               airesponse = OpenAIText.OpenAITextResponse('Summarize data for skills in max 50 words',listOfContent[count]['content'])
               returnSkillsCV = SkillExtractorDetails.GetSkillData(skill_extractor,airesponse) 
               myDictCV[listOfContent[count]['name']] = returnSkillsCV   
                   
   myDictJD = {} 
   myDictJD["JD1"] = returnSkills
   
   
   data = SkillMatch.SkillMatchResult(model,myDictJD,myDictCV)
   print(airesponse)
   #print(exp)
   return data



@app.get("/GetOpenAPIResponse/")
def GetOpenAPIResponse(query:str, content:str):
    return OpenAIText.OpenAITextResponse(query,content)
    
#return JSONResponse(content={"message": "Here's your interdimensional portal." , "mes1":"data2"})

#https://vaibhav84-hackerspaceapi.hf.space/docs
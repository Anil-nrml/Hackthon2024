import pandas as pd
from sentence_transformers import SentenceTransformer, util
class SkillMatch:
    def SkillMatchResult(model,jd_skills,cv_skills):
        count = 0
        TopScore = 0
        CourseId = 0
        datalist = []
        for jd in jd_skills:
            for cv in cv_skills:
            #if(cv in match_data[1] and jd in match_data[0]):
            #print("Already record : " + str(cv) + " , "  + str(jd))
              
                #print(match_details)  
                print("Running Matching Algo")
                count += 1
                sentence1 = " ".join(cv_skills[cv])
                sentence2 = " ".join(jd_skills[jd])
                embedding1 = model.encode(sentence1, convert_to_tensor=True)
                embedding2 = model.encode(sentence2, convert_to_tensor=True)

                # Compute cosine similarity between the two sentence embeddings
                cosine_similarit = util.cos_sim(embedding1, embedding2)
                datalist.append(cv + " : Score : " + str(cosine_similarit[0][0].item()))            
                
                
        return  datalist
    
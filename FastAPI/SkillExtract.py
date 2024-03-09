import psycopg2
from psycopg2 import sql
import pandas as pd
import re
class SkillExtractorDetails:

    def GetSkillId(skillname,jdmasterid,db_params):    
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
    def getNewSkills(db_params):
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
    def extractWords(job_description,JdMasterid,db_params):
        job_roles = []
        job_description = job_description.replace(')',' ')
        delimiters = ",", " ", " , ", ";","\n","/","\\"
        regex_pattern = '|'.join(map(re.escape, delimiters))
        df = SkillExtractorDetails.getNewSkills(db_params)
        data = re.split(regex_pattern, job_description)
        #data = job_description.split(',')
        for ds in data:
            #print(ds)
            try:
                if(SkillExtractorDetails.skill_Validate(df,ds.strip())):                
                    job_roles.append(ds) 
                    SkillExtractorDetails.GetSkillId(ds.strip(),JdMasterid,db_params)
                    print("Skills Identified* : " + ds)   
            except Exception as error:
                test = 1
        return job_roles 
    def SkillExtract(db_params,skill_extractor,JdID):
        print("Extracting Skills for the JD...")
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        jd_id = str(JdID)
        # Retrieve "id" and "description" columns from the table
        #query = sql.SQL("select jdmasterid,jobdescription from JDMaster where isskillsextracted in (0)")
        query = "select jdmasterid,jobdescription,filename from JDMaster where isskillsextracted = 0 and jdmasterid ="+ jd_id 

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
            SkillExtractorDetails.extractWords(description_value,id_value,db_params)
            query = "update public.jdmaster set isskillsextracted = 1 where jdmasterid = (%s)"
            
            params = (id_value,)  
            cursor.execute(query, params)
            conn.commit()
            print("Skills Updated for Skills Extraction for file ", filename_jd)
            print("Total Skills : ", len(skills_list))
            return SkillExtractorDetails.latestSkillDetails(id_value,db_params)
    def latestSkillDetails(jid,db_params):
        data = ""
        data = SkillExtractorDetails.display_skills(jid,db_params)
        #    jid = df.iat[0,0]
        return data
    def tuple_to_int(tup):
        if len(tup) == 1:
            return tup[0]
        else:
            return tup[0] * (10 ** (len(tup) - 1)) + SkillExtractorDetails.tuple_to_int(tup[1:])


    def skill_check(dbQuery,db_params):
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        df = pd.read_sql_query(dbQuery, conn)
        Required_Skills=''
        for index, row in df.iterrows():   
        
            skillname = row['skillname']
            Required_Skills = Required_Skills + ', '+ skillname
        
        Required_Skills = Required_Skills[2:] 
        return Required_Skills
    def display_skills(id, db_params):
        jd=str(id)
        query = "select skillname from SkillDetails  where id = "+ jd +" and skillscore > 99 and skilltype = 'Hard Skill'"
        RequiredSkills_Hard  = SkillExtractorDetails.skill_check(query,db_params)

        query = "select skillname from SkillDetails  where id = "+ jd +" and skillscore > 50 and skilltype = 'Soft Skill'"  
        RequiredSkills_Soft  = SkillExtractorDetails.skill_check(query,db_params)

        query = "select skillname from SkillDetails  where id = "+ jd +" and skillscore < 50 and skilltype = 'Soft Skill'"  
        RequiredSkills_G1  = SkillExtractorDetails.skill_check(query,db_params)

        query = "select skillname from SkillDetails  where id = "+ jd +" and skillscore < 99 and skilltype = 'Hard Skill'"  
        RequiredSkills_G2  = SkillExtractorDetails.skill_check(query,db_params)

        print('')
        print("Required Skills      : " + RequiredSkills_Hard)
        print('')
        print("Required Soft Skills : " + RequiredSkills_Soft)
        print('')
        print("Good to have Skills  : " + RequiredSkills_G1 +  " " + RequiredSkills_G2)
        return RequiredSkills_Hard + "@" + RequiredSkills_Soft + "@" + RequiredSkills_G1 + " " + RequiredSkills_G2

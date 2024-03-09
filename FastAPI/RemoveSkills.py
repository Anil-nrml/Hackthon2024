import psycopg2
class RemoveSkill:
    def RemoveSkillDetails(db_params, SkillName):
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()          
        print("Removing Skills " +  SkillName)
        query = "update skillmaster set weightage = 0 where upper(skilldetails) = (%s)"        
        params = (SkillName.upper(),)  
        cursor.execute(query, params)
        conn.commit()
        cursor.close()
        conn.close() 
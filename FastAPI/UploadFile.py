from datetime import date
import psycopg2
from psycopg2 import sql
import pandas as pd

class UploadOpenFile:

    def uploadFile(text,filePath,db_params):

        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()    
        query = "Select max(jdmasterid) from JdMaster"                
        df = pd.read_sql_query(query, conn)
        try:
            MasterId = df.iat[0,0] + 1
        except:
            MasterId =1

        print(MasterId)
        query =sql.SQL("""INSERT INTO  JDMaster (jdmasterid,jobdescription, filename, UploadedDate, IsDetailsExtracted,IsSkillsExtracted,source) VALUES (%s,%s,%s,%s,%s,%s,%s)""")
        cursor.execute(query, (MasterId,text,filePath, date.today(),0,0,"JD")) 
        conn.commit()
        cursor.close()
        conn.close()
        print("File Uploaded...")
        return MasterId
        
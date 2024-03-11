import streamlit as st
import psycopg2
from psycopg2 import sql
import pandas as pd
db_params = {
    'host': 'dpg-cnhir5fsc6pc73dvj380-a.oregon-postgres.render.com',
    'database': 'OpenAI',
    'user': 'anu',
    'password': '5omRLogf9Kdas3zoBFPCT9yrCGU4IbEX',
}

title = st.text_input('Enter Skills to search Profiles', 'Skills')

ProfileType = st.radio(
    "Select Profile / Job Description to Search",
    ["Job Description", "Profile"])


def ShowResults(title):
    if(title == ''):
        if(ProfileType == 'Profile'):
            dbQuery = "select * from SearchProfile"
        else:
            dbQuery = "select * from SearchJD"
    else:
        if(ProfileType == 'Profile'):
            data= ""
            if(title.find(',') == -1):                
                dbQuery = "select * from SearchProfile where upper(skilldetails) like ('%" + str(title).upper() + "%')"
            else:
                strs = title.split(',')    
                for x in strs:
                    data =  data + "upper(skilldetails) like ('%" + str(x).upper() + "%') or "
                data1 = data[:-3]    
                dbQuery  = "select * from SearchProfile where " + data1    
        else:            
            data= ""
            if(title.find(',') == -1):                
                dbQuery = "select * from SearchJD where upper(skilldetails) like ('%" + str(title).upper() + "%')"
            else:
                strs = title.split(',')    
                for x in strs:
                    data =  data + "upper(skilldetails) like ('%" + str(x).upper() + "%') or "
                data1 = data[:-3]    
                dbQuery  = "select * from SearchJD where " + data1    

    conn = psycopg2.connect(**db_params)   
    df = pd.read_sql_query(dbQuery, conn)

    
    st.dataframe(df,use_container_width = True, hide_index = True) 

ShowResults(title)
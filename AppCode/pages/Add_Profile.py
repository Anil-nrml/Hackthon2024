import streamlit as st
from PyPDF2 import PdfReader
import numpy as np
import numpy
from io import StringIO 
import requests
import json  
def submit (uploaded_resume):
    text = ""
    fName = ""   
    if (uploaded_resume):
        
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
            inputs = {"text" : text, "filename" : fName}         
        
            test_url = "https://vaibhav84-resumeapi.hf.space/UploadProfileOpenText"
            test_response = requests.get(test_url, inputs)

            #st.write(test_response.json())
            print(test_response.json())
            st.success('File uploaded successfully')    

def main():
    st.header("Best Resume Matching Engine")

    form = st.form(key='some_form')
    uploaded_resume = form.file_uploader("Upload Profile Description" , type = ["txt","pdf"])    
    form.form_submit_button("Run", on_click=submit(uploaded_resume=uploaded_resume))

if __name__ == '__main__':
    main()


import streamlit as st
import requests
from io import StringIO 
from PyPDF2 import PdfReader
from WebAPI import WebAPIURL
st.set_page_config(
    page_title="Home",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded" 
)

with st.sidebar:
    st.title("Best Resume Fit Matching Engine")
    st.markdown('''
    ## About
    Goal is to match the input profile with Job Descriptions and rank them with best match score
    ''')
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
            inputs = {"text" : text, "filename" : fName}         
            api_url = WebAPIURL.GetWebAPIURL('UploadJobDescriptionOpenText')
            #test_url = "https://vaibhav84-resumeapi.hf.space/UploadJobDescriptionOpenText"
            test_response = requests.get(api_url, inputs)

            #st.write(test_response.json())
            print(test_response.json())
            st.success(test_response.json())    
        #AppFlow(text,fName,query, True)
     
           


def main():
    st.header("Best Resume Matching Engine")

    form = st.form(key='some_form')
    uploaded_resume = form.file_uploader("Upload Job Description" , type = ["txt","pdf"])
    form.form_submit_button("Run", on_click=submit(uploaded_resume=uploaded_resume))

if __name__ == '__main__':
    main()

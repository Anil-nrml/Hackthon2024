import streamlit as st
from streamlit_lottie import st_lottie
import json
import requests

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def load_lottieFile(filePath: str):
    with open(filePath,'r') as f:
        return json.load(f)
    
        
class Animation: 

    def get_login_anime():
        login_anime = load_lottieFile("Anime/Animation_login.json")
        st_lottie(login_anime, key="login")

    def get_sidebar_anime(inputkey: str):
        robo_anime = load_lottieFile("Anime/Animation_robo.json")
        st_lottie(robo_anime, key=inputkey)

    def get_sidebar(inputkey: str):
        with st.sidebar:
            Animation.get_sidebar_anime(inputkey)
            st.title("Best Resume Fit Matching Engine")
            st.markdown('''
            ## About
            Goal is to match the input profile with Job Descriptions and rank them with best match score
            ''')

    def get_loader(inputkey: str):
        loader_anime = load_lottieFile("Anime/Animation_file_transfer.json")
        st_lottie(loader_anime, key=inputkey)



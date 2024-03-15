import streamlit as st
import requests
from io import StringIO 
from PyPDF2 import PdfReader
from WebAPI import WebAPIURL
from AppConfiguration import Animation
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Home",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded" 
    #initial_sidebar_state="collapsed" 
)

st.markdown("""
<style>
    #header {
        visibility: hidden;
    }
    .st-emotion-cache-z5fcl4{
            padding: 1rem 5rem 0 5rem
    }
</style>
""", unsafe_allow_html=True)

data = {
    "Technology": ["Artificial Intelligence", "Machine Learning", "Cloud Computing", "Cybersecurity", "Data Science"],
    "Trend Score": [80, 90, 70, 85, 95]
}

df = pd.DataFrame(data)

def login():
    st.title("Resume Matcher")
    col1, col2 = st.columns([5, 5])

    # Left column for Lottie animation
    with col1:        
        Animation.get_login_anime()

    with col2:
        with st.form("login_form"):
            # Login form
            st.title("Login")
            username = st.text_input("Username", value="", key='username')
            password = st.text_input("Password", type="password", value="", key='password')
            submitted = st.form_submit_button("Submit")
            if submitted:
                if username == "admin" and password == "pwd":
                    st.success("Logged in successfully!")
                    st.session_state["current_page"] = "main"
                    st.session_state["logged_in"] = True
                    st.experimental_rerun()

                else:
                    st.error("Invalid username or password. Please try again.")
            st.write("</div>", unsafe_allow_html=True)
      
def dashboard():
    Animation.get_sidebar("dashboard")
    st.title("Top Trending Technologies")
    create_trend_chart()

def create_trend_chart():
    plt.figure(figsize=(10, 6))
    plt.barh(df["Technology"], df["Trend Score"], color='skyblue')
    plt.xlabel("Trend Score")
    plt.ylabel("Technology")
    #plt.title("Top Trending Technologies")
    plt.gca().invert_yaxis()  # Invert y-axis to display highest score at top
    plt.grid(axis='x', linestyle='--', alpha=0.6)
    plt.tight_layout()
    st.pyplot(plt)

if __name__ == '__main__':
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "login"

    if st.session_state["current_page"] == "login":
        login()
    elif st.session_state["current_page"] =="main":
        dashboard()
    else:
        dashboard()

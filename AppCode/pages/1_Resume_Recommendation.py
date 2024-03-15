import streamlit as st
import json
from AppConfiguration import Animation
import time

st.set_page_config(
    page_title="Resume",
    page_icon="🧊",
    layout="wide",
    #initial_sidebar_state="expanded" 
    initial_sidebar_state="auto" 
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

def read_api_response():
    
    #Animation.get_loader()
    #st.snow()
    #with st.spinner(Animation.get_loader('resume_loader')):
    with st.spinner('loading...'):
        time.sleep(5)
    file = open('sample_response.json')
    json_data = json.load(file)

    # To print the empty line
    st.write('---')
    df = json_data['results']
    if df:
        st.dataframe(df,use_container_width = True, hide_index = True) 

def main():
    st.title("Resume Recommendation")

    with st.form("resume_form"):
        # Create a form with two columns
        col1, col2 = st.columns(2)

        with col1:
            context = st.text_input("Context", '')
            threshold = st.slider("Threshold", min_value=0.1, max_value=1.0, value=0.7, step=0.01)
            input_path = st.text_input("Input Path", '')

        # Add controls to the second column
        with col2:
            category = st.text_input("Category", 'resume')
            no_of_matches = st.number_input("No. of Matches", min_value=1, value=3)

    
        submit_button = st.form_submit_button("Submit")
        if submit_button:
            # Validate if all fields are filled
            if context.strip() == "" or category.strip() == "" or input_path.strip() == "":
                st.error("Please fill in all fields.")
            else:
                # Generate a JSON based on user inputs
                data_to_post = {
                    "context": context,
                    "category": category,
                    "threshold": threshold,
                    "noOfMatches": no_of_matches,
                    "inputPath": input_path
                }

                # Add api call
                #st.json(data_to_post)
                read_api_response()
   
 
# main()

if __name__ == '__main__':
    if not st.session_state.get("logged_in", False):
        st.error("You must be logged in to access this page.")
        st.stop()
    else:
        Animation.get_sidebar("resume")  
        main()

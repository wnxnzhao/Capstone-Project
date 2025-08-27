

# Set up and run this Streamlit App
import streamlit as st
import pandas as pd
from logics.query_handler import process_user_message
from helper_functions.utility import check_password  


# region <--------- Streamlit App Configuration --------->
st.set_page_config(
    layout="centered",
    page_title="Energy Saver Advisor"
)
# endregion <--------- Streamlit App Configuration --------->

st.title("Energy Saver Advisor")

# Check if the password is correct.  
if not check_password():  
    st.stop()

st.expander("""

IMPORTANT NOTICE: This web application is a prototype developed for educational purposes only. The information provided here is NOT intended for real-world usage and should not be relied upon for making any decisions, especially those related to financial, legal, or healthcare matters.

Furthermore, please be aware that the LLM may generate inaccurate or incorrect information. You assume full responsibility for how you use any generated output.

Always consult with qualified professionals for accurate and personalized advice.

""")

form = st.form(key="form")
form.subheader("WattSaver: Your Friendly Energy Advisor")

user_prompt = form.text_area("Not sure how to save energy in your households? Enter your questions here and WattSaver will answer!", height=200)

if form.form_submit_button("Submit"):
    
    st.toast(f"User Input Submitted - {user_prompt}")

    st.divider()

    response = process_user_message(user_prompt)
    st.write(response)



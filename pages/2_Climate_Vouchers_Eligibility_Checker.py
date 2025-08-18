import streamlit as st
import pandas as pd
import os
import json
import openai
from dotenv import load_dotenv
from openai import OpenAI
import tiktoken
import random  
import hmac

# region <--------- Streamlit App Configuration --------->
st.set_page_config(
    layout="centered",
    page_title="Energy Saver Advisor"
)
# endregion <--------- Streamlit App Configuration --------->

st.title("Climate Vouchers Eligibility Checker")
st.image("https://www.climate-friendly-households.gov.sg/images/main logo.jpg", width = 300)

def check_password():  
    """Returns `True` if the user had the correct password."""  
    def password_entered():  
        """Checks whether a password entered by the user is correct."""  
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):  
            st.session_state["password_correct"] = True  
            del st.session_state["password"]  # Don't store the password.  
        else:  
            st.session_state["password_correct"] = False  
    # Return True if the passward is validated.  
    if st.session_state.get("password_correct", False):  
        return True  
    # Show input for password.  
    st.text_input(  
        "Password", type="password", on_change=password_entered, key="password"  
    )  
    if "password_correct" in st.session_state:  
        st.error("😕 Password incorrect")  
    return False

# Check if the password is correct.  
if not check_password():  
    st.stop()

st.header("Are you eligible for the Climate Vouchers?")
st.caption("Select the applicable option for all 4 buttons below to check your eligibility for the Climate Vouchers under the Climate Friendly Households Programme.")
col1, col2, col3, col4 = st.columns(4)
with col1:
    residential_status = st.radio(
        "What is your residential status?",
        ["Singapore Citizen", "Permanent Resident", "Others"]
    )
with col2:
    property_type = st.radio(
        "What is your property type?",
        ["HDB", "Private Residential Property"]
    )
with col3:
    claimed_status_300 = st.radio(
        "Have you claimed the 300 SGD Climate Vouchers?",
        ["Yes", "No"]
    )
with col4:
    claimed_status_100 = st.radio(
        "Have you claimed the 100 SGD Climate Vouchers?",
        ["Yes", "No"]
    )

if residential_status == "Singapore Citizen":
    if claimed_status_300 == "No" and claimed_status_100 == "No":
        st.write("You are eligible for both the 300 SGD and 100 SGD Climate Vouchers.")
    elif claimed_status_300 == "No" and claimed_status_100 == "Yes":
        st.write("You are eligible for the 300 SGD Climate Vouchers.")
    elif claimed_status_300 == "Yes" and claimed_status_100 == "No":
        st.write("You are eligible for the 100 SGD Climate Vouchers.")
    else:
        st.write("You have claimed all of the Climate Vouchers!")

if residential_status == "Permanent Resident":
    if property_type != "HDB":
        st.write("You are not eligible for the Climate Vouchers.")
    elif property_type == "HDB":
        if claimed_status_300 == "No" and claimed_status_100 == "No":
            st.write("You are eligible for both the 300 SGD and 100 SGD Climate Vouchers.")
        elif claimed_status_300 == "No" and claimed_status_100 == "Yes":
            st.write("You are eligible for the 300 SGD Climate Vouchers.")
        elif claimed_status_300 == "Yes" and claimed_status_100 == "No":
            st.write("You are eligible for the 100 SGD Climate Vouchers.")
    else:
        st.write("You are not eligible for the Climate Vouchers.")

if residential_status == "Others":
    st.write("You are not eligible for the Climate Vouchers.")

st.divider()

# Load the JSON file
filepath = './data/eligible_products.json'
with open(filepath, 'r') as file:
    json_string = file.read()
    dict_of_products = json.loads(json_string)

if load_dotenv('.env'):
   # for local development
   OPENAI_KEY = os.getenv('OPENAI_API_KEY')
else:
   OPENAI_KEY = st.secrets['OPENAI_API_KEY']

# Pass the API Key to the OpenAI Client
client = OpenAI(api_key=OPENAI_KEY)

def get_embedding(input, model='text-embedding-3-small'):
    response = client.embeddings.create(
        input=input,
        model=model
    )
    return [x.embedding for x in response.data]


# This is the "Updated" helper function for calling LLM
def get_completion(prompt, model="gpt-4o-mini", temperature=0, top_p=1.0, max_tokens=1024, n=1, json_output=False):
    if json_output == True:
      output_json_structure = {"type": "json_object"}
    else:
      output_json_structure = None

    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create( #originally was openai.chat.completions
        model=model,
        messages=messages,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        n=1,
        response_format=output_json_structure,
    )
    return response.choices[0].message.content


# Note that this function directly take in "messages" as the parameter.
def get_completion_by_messages(messages, model="gpt-4o-mini", temperature=0, top_p=1.0, max_tokens=1024, n=1):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        n=1
    )
    return response.choices[0].message.content


# This function is for calculating the tokens given the "message"
# ⚠️ This is simplified implementation that is good enough for a rough estimation
def count_tokens(text):
    encoding = tiktoken.encoding_for_model('gpt-4o-mini')
    return len(encoding.encode(text))


def count_tokens_from_message(messages):
    encoding = tiktoken.encoding_for_model('gpt-4o-mini')
    value = ' '.join([x.get('content') for x in messages])
    return len(encoding.encode(value))


def identify_product_category(user_message):
    delimiter = "####"

    system_message = f"""
    You will be provided with customer service queries.
    Follow these instructions to answer the customer queries.
    The customer query will be delimited with a pair {delimiter}.

    Decide if the query is relevant to any specific products\
    in the Python dictionary below, which each key is a `product category`\
    and the value is the `requirements` of the eligible products.
    Some of the product categories have a list of ticks that the product must have on the energy label to be eligible for the Climate Vouchers.
    The more ticks, the more you save.
    Additional `remarks` are also provided for some of the product categories, especially those without energy labels.

    You must only rely on the information in the products information in the Python dictionary.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    Your response should be as detail as possible and include information that is useful for customer to better understand the eligible product.

    Answer the customer in a friendly tone.
    Make sure the statements are factually accurate.
    If there are any relevant product found, output the `product category` and the associated `requirements` into in a tidy and readable format.
    For those product categories that have an empty list for number of ticks, inform the user that the product do not carry any energy label.
    Use Neural Linguistic Programming to construct your response.
    Always include at the end of the response that 'Given that retailers may offer different models, it is advisable to enquire with them about the specific models that are eligible for purchase with the Climate Vouchers.'.
    {dict_of_products}
    If there are no relevant product found, ask the user to be more specific and provide more details about the product.
      
    Ensure that your response is readable and without any enclosing tags or delimiters.
    """

    messages =  [
        {'role':'system',
         'content': system_message},
        {'role':'user',
         'content': f"{delimiter}{user_message}{delimiter}"},
    ]

    response_to_user = get_completion_by_messages(messages)
    return response_to_user

form = st.form(key="form")
form.subheader("Eligible Product Checker")

user_prompt = form.text_area("Not sure which products are covered under the Climate Vouchers? Enter your questions here to find out!", height=200)
if form.form_submit_button("Submit"):
    
    st.toast(f"User Input Submitted - {user_prompt}")

    response = identify_product_category(user_prompt)
    st.write(response)

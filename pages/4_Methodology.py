import streamlit as st

# region <--------- Streamlit App Configuration --------->
st.set_page_config(
    layout="centered",
    page_title="Energy Saver Advisor"
)
# endregion <--------- Streamlit App Configuration --------->

st.title("Methodology")

st.header("WattSaver: Your Friendly Energy Advisor")
st.write("Langchain Chroma is used to create a RAG chain that can answer questions related to energy saving and advice on how to improve energy efficiency in households by providing useful tips.\
         Input documents are text files containing information extracted from the NEA Energy Efficiency Household Sector and Climate Friendly Households Programme websites.\
         The documents are split into smaller chunks using RecursiveCharacterTextSplitter, and then embedded using the OpenAI text-embedding-3-small model.\
         As a way to improve the post-retrieval process, identified chunks are filtered based on a threshold.")

st.header("Climate Vouchers Eligibility Checker")
st.write("The eligible products that can be purchased with the Climate Vouchers under the Climate Friendly Households Programme are stored in a JSON file.\
         A simple rule-based approach is performed using radio buttons on Streamlit to determine if the user is eligible for Climate Vouchers based on their residential status, property type, and claimed status of the vouchers.\
         Similarly, a simple RAG pipeline was used to check if a relevant product is found in the JSON file based on the user's input.\
         The product information and requirements for use of Climate Vouchers are returned in a tidy format")

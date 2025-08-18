import streamlit as st

# region <--------- Streamlit App Configuration --------->
st.set_page_config(
    layout="centered",
    page_title="Energy Saver Advisor"
)
# endregion <--------- Streamlit App Configuration --------->

st.title("About this App")
st.expander("""

IMPORTANT NOTICE: This web application is a prototype developed for educational purposes only. The information provided here is NOT intended for real-world usage and should not be relied upon for making any decisions, especially those related to financial, legal, or healthcare matters.

Furthermore, please be aware that the LLM may generate inaccurate or incorrect information. You assume full responsibility for how you use any generated output.

Always consult with qualified professionals for accurate and personalized advice.

""")
st.image("https://www.climate-friendly-households.gov.sg/images/main logo.jpg")

st.header("Project Scope")
st.write("Singapore is working towards reducing its greenhouse gas emissions by using less carbon-intensive fuels, and by improving energy efficiency.\
         In order to reduce its greenhouse gas emissions, Singapore has switched from carbon-intensive fuel oil to natural gas for electricity generation.\
         However, there are limits to how much further Singapore can reduce its emissions. Therefore, improving energy efficiency remains a key focus for Singapore.\
         To achieve this goal, it requires a collective support and effort from all sectors of Singapore, including households.\
         \
         To foster a climate-friendly mindset among households, the Climate Friendly Households Programme (CFHP) was launched in November 2020 and later enhanced from 15 April 2024 to include all HDB households.\
         Recently, the CFHP was again expanded in Apr 2025 to Singapore Citizen registered and residing at a private residential property.\
         Each eligible household is entitled to one set of $300 vouchers and one set of $100 vouchers.\
         The Climate Vouchers can be used to purchase 10 types of energy- and water-efficient household products.\
         By switching to more efficient appliances and fittings, households can reduce their energy and/or water consumption, lower their utility bills, reduce greenhouse gas emissions, and play their part in slowing down climate change.")

st.header("Objectives")
st.write("This app aims to 1) provide households with energy saving tips and advice on how to improve energy efficiency , and 2) check if a product could be purchased with the Climate Vouchers through an interactive interface. \
          The app will allow users to ask questions related to energy saving and eligible products under the the Climate Friendly Households Programme, and provide them with relevant information and suggestions.")

st.header("Data Sources")
st.write("All data used for this app are publicly available information taken from the NEA Energy Efficiency Household Sector and Climate Friendly Households Programme websites.")
col1, col2 = st.columns(2)
with col1:
       st.link_button("NEA Energy Efficiency Household Sector Webpage", "https://www.nea.gov.sg/our-services/climate-change-energy-efficiency/energy-efficiency/household-sector")
with col2:
       st.link_button("Climate Friendly Households Programme Webpage", "https://www.climate-friendly-households.gov.sg/")

st.header("Features")
st.write("This app has two main features: \
            1) WattSaver: Your Friendly Energy Advisor - An LLM-based AI Assistant that can respond to users' queries related to energy saving and advice on how to improve energy efficiency in their households by providing useful tips,\
            2) Climate Vouchers Eligibility Checker - An LLM-based AI Assistant that can check if a product is eligible for purchase with the Climate Vouchers under the Climate Friendly Households Programme.")

st.subheader("How to Use")
st.write("The steps to using either features of this app are straightforward and simple:\
            1. Enter your prompt in the text area.\
            2. Click the 'Submit' button.\
            3. The app will generate a text completion based on your prompt.")



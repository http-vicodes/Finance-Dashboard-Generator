import streamlit as st
import pandas as pd
import plotly.express as px
import json
import io
import os


st.set_page_config(page_title="Financial Dashboard Generator", page_icon="🏦", layout="wide") #this allows us to set the title of the page and other configurations

def load_transactions(file):
    try:
        df = pd.read_csv(file) # pandas can read csv files directly
        df.columns = [col.strip() for col in df.columns] # pandas can grab all the columns in a dataframe. Then with the strip() method is removes any leading or trailing whitespace from each column name.
        df["Amount"] = 
        st.write(df)
        return df
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")

def main():
    st.title("Finance Dashboard Generator")
    uploaded_file = st.file_uploader("Upload your transaction CSV file", type=["csv"])

    if uploaded_file is not None:
        df = load_transactions(uploaded_file)


main()
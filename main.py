import streamlit as st
import pandas as pd
import plotly.express as px
import json
import io
import os


st.set_page_config(page_title="Financial Dashboard Generator", page_icon="🏦", layout="wide") #this allows us to set the title of the page and other configurations

categories_file = "categories.json"

if "categories" not in st.session_state: # this is the stremlit way to save state sessions across reruns
    st.session_state.categories = {
        "Uncategorized": []
    }
    
if os.path.exists("categories.json"):
    with open("categories.json", "r") as f:
        st.session_state.categories = json.load(f)
        
def save_categories():
    with open("categories.json", "w") as f:
        json.dump(st.session_state.categories, f)

def load_transactions(file):
    try:
        df = pd.read_csv(file) # pandas can read csv files directly
        df.columns = [col.strip() for col in df.columns] # pandas can grab all the columns in a dataframe. Then with the strip() method is removes any leading or trailing whitespace from each column name.
        df["Amount"] = df["Amount"].str.replace(",", "").astype(float) # Pandas operation that takes in the value of amount column, coverts them into a string, removes the commas by replacing them with spaces and finally coverts it back into a float
        df["Date"] = pd.to_datetime(df["Date"], format="%d %b %Y")
        return df
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")

def main():
    st.title("Finance Dashboard Generator")
    uploaded_file = st.file_uploader("Upload your transaction CSV file", type=["csv"])

    if uploaded_file is not None:
        df = load_transactions(uploaded_file)
        
        if df is not None:
            debits_df = df[df["Debit/Credit"] == "Debit"].copy() #dataframe filter operation in Pasndas
            credits_df = df[df["Debit/Credit"] == "Credit"].copy()
            
            
            tab1, tab2 = st.tabs(["Expenses (Debits)", "Payments (Credits)"])
            with tab1:
                new_category = st.text_input("New Category Name")
                add_button = st.button("Add Category")
                
                if add_button and new_category:
                    if new_category not in st.session_state.categories:
                        st.session_state.categories[new_category] = []
                        save_categories()
                        st.rerun() # this forces the app to rerun and reflect the changes
                
                st.write(debits_df)
                
            with tab2: 
                st.write(credits_df)

            
main()
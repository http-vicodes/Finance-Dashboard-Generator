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
        
def categorize_transactions(df):
    df["Category"] = "Uncategorized" # makes the default category uncategorized to start
    
    for category, keywords in st.session_state.categories.items():
        if category == "Uncategorized" or not keywords:
            continue
        
        lowered_keywords = [keyword.lower().strip() for keyword in keywords]
        
        for idx, row in df.iterrows():
            details = row["Details"].lower()
            if details in lowered_keywords:
                df.at[idx, "Category"] = category
    return df

def load_transactions(file):
    try:
        df = pd.read_csv(file) # pandas can read csv files directly
        df.columns = [col.strip() for col in df.columns] # pandas can grab all the columns in a dataframe. Then with the strip() method is removes any leading or trailing whitespace from each column name.
        df["Amount"] = df["Amount"].str.replace(",", "").astype(float) # Pandas operation that takes in the value of amount column, coverts them into a string, removes the commas by replacing them with spaces and finally coverts it back into a float
        df["Date"] = pd.to_datetime(df["Date"], format="%d %b %Y")
        return categorize_transactions(df)
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")

def add_keyword_to_category(category, keyword):
    keyword = keyword.strip()
    if keyword and keyword not in st.session_state.categories[category]:
        st.session_state.categories[category].append(keyword)
        save_categories()
        return True
    return False

def main():
    st.title("Finance Dashboard Generator")
    uploaded_file = st.file_uploader("Upload your transaction CSV file", type=["csv"])

    if uploaded_file is not None:
        df = load_transactions(uploaded_file)
        
        if df is not None:
            debits_df = df[df["Debit/Credit"] == "Debit"].copy() #dataframe filter operation in Pasndas
            credits_df = df[df["Debit/Credit"] == "Credit"].copy()
            
            st.session_state.debits_df = debits_df.copy()
            
            tab1, tab2 = st.tabs(["Expenses (Debits)", "Payments (Credits)"])
            with tab1:
                new_category = st.text_input("New Category Name")
                add_button = st.button("Add Category")
                
                if add_button and new_category:
                    if new_category not in st.session_state.categories:
                        st.session_state.categories[new_category] = []
                        save_categories()
                        st.rerun() # this forces the app to rerun and reflect the changes
                
                st.subheader("Your Expenses")
                edited_df = st.data_editor(
                    st.session_state.debits_df[["Date", "Details", "Amount", "Category"]],
                    column_config={
                        "Date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
                        "Amount": st.column_config.NumberColumn("Amount", format="%.2F, AED"),
                        "Category": st.column_config.SelectboxColumn(
                            "Category",
                            options=list(st.session_state.categories.keys())
                        )
                    },
                    hide_index=True,
                    use_container_width=True,
                    key="category_editor"
                )
                
                save_button = st.button("Apply Changes", type="primary")
                
                # if the save button is clicked, we loop through the edited dataframe and check if any categories have changed in the web page UI. If they have, we update the original dataframe and add the keyword to the category
                if save_button:
                    for idx, row in edited_df.iterrows():
                        new_category = row["Category"]
                        if row["Category"] == st.session_state.debits_df.at[idx, "Category"]:
                            continue
                        
                        details = row["Details"]
                        st.session_state.debits_df.at[idx, "Category"] = new_category
                        add_keyword_to_category(new_category, details)
                
                st.subheader("Expenses Summary")
                category_totals = st.session_state.debits_df.groupby("Category")["Amount"].sum().reset_index() # pandas groupby operation that groups the dataframe by category and sums the amounts for each category which is almost SQL like
                category_totals = category_totals.sort_values("Amount", ascending=False)
                
                st.dataframe(category_totals,
                             column_config={
                                 "Amount": st.column_config.NumberColumn("Amount", format="%.2F, AED")
                             },
                             use_container_width=True,
                             hide_index=True
                             )
                
                fig = px.pie( #plotly express pie chart formula => .pie(data_frame, values, names, title)
                    category_totals,
                    values="Amount",
                    names="Category",
                    title="Expenses by Category"
                    
                )
                
                st.plotly_chart(fig, use_container_width=True) # plotly chart rendering in streamlit
                      
            with tab2: 
                st.subheader("Payment Summary")
                total_paymenta = credits_df["Amount"].sum()
                st.metric("Total Payments", f"{total_paymenta:,.2f} AED")
                st.write(credits_df)

            
main()
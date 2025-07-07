import streamlit as st
import requests
import pandas as pd
import datetime

st.set_page_config(page_title="Codeforces User Dashboard", layout="wide")
st.title("📊 Codeforces User Dashboard")

# Load data from API
@st.cache_data(show_spinner=True)
def fetch_users():
    url = "https://codeforces.com/api/user.ratedList?activeOnly=false"
    r = requests.get(url)
    data = r.json()
    if data['status'] != 'OK':
        st.error("Failed to fetch data from Codeforces API.")
        return pd.DataFrame()
    
    users = data['result']
    df = pd.DataFrame(users)
    df['registrationDate'] = pd.to_datetime(df['registrationTimeSeconds'], unit='s')
    return df

with st.spinner("Loading user data from Codeforces..."):
    df = fetch_users()

# Sidebar Filters
st.sidebar.header("🔍 Filters")

# Country Filter
country_list = sorted(df['country'].dropna().unique().tolist())
selected_country = st.sidebar.selectbox("Country", ['All'] + country_list)

# Rank Filter
rank_list = sorted(df['rank'].dropna().unique().tolist())
selected_rank = st.sidebar.selectbox("Rank", ['All'] + rank_list)

# Registration Date Filter
min_date = df['registrationDate'].min().date()
max_date = df['registrationDate'].max().date()
date_range = st.sidebar.date_input("Registration Date Range", [min_date, max_date])

# Apply filters
filtered_df = df.copy()

if selected_country != 'All':
    filtered_df = filtered_df[filtered_df['country'] == selected_country]

if selected_rank != 'All':
    filtered_df = filtered_df[filtered_df['rank'] == selected_rank]

filtered_df = filtered_df[
    (filtered_df['registrationDate'] >= pd.to_datetime(date_range[0])) &
    (filtered_df['registrationDate'] <= pd.to_datetime(date_range[1]))
]

# Display results
st.markdown(f"### Showing {len(filtered_df)} users")

st.dataframe(
    filtered_df[['handle', 'rank', 'rating', 'maxRank', 'country', 'contribution', 'registrationDate']].sort_values(
        by='rating', ascending=False
    ),
    use_container_width=True
)

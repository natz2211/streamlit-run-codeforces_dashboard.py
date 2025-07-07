import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Codeforces User Dashboard", layout="wide")
st.title("📊 Codeforces User Dashboard")

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

    # Enrich the data
    df['registrationDate'] = pd.to_datetime(df['registrationTimeSeconds'], unit='s')
    df['profile'] = df['handle'].apply(lambda h: f"https://codeforces.com/profile/{h}")

    # Create full name column
    df['fullName'] = df[['firstName', 'lastName']].fillna('').agg(' '.join, axis=1).str.strip()
    df.loc[df['fullName'] == '', 'fullName'] = '—'

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

filtered_df = filtered_df.sort_values(by='rating', ascending=False)

# Pagination
st.sidebar.markdown("### 📄 Pagination")
page_size = st.sidebar.number_input("Users per page", min_value=10, max_value=500, value=100, step=10)
total_pages = (len(filtered_df) - 1) // page_size + 1

page_numbers = [f"Page {i+1}" for i in range(total_pages)]
selected_page_label = st.sidebar.selectbox("Select Page", page_numbers)
page = page_numbers.index(selected_page_label) + 1

start_idx = (page - 1) * page_size
end_idx = start_idx + page_size
paginated_df = filtered_df.iloc[start_idx:end_idx]

# Columns to display (email and contribution removed)
columns_to_display = [
    'handle', 'fullName', 'rank', 'rating', 'maxRank',
    'country', 'city', 'organization', 'registrationDate', 'profile'
]

column_names = {
    'handle': 'Handle',
    'fullName': 'Full Name',
    'rank': 'Rank',
    'rating': 'Rating',
    'maxRank': 'Max Rank',
    'country': 'Country',
    'city': 'City',
    'organization': 'Organization',
    'registrationDate': 'Registration Date',
    'profile': 'Profile URL'
}

# Make profile URL clickable
paginated_df['Profile URL'] = paginated_df['profile'].apply(
    lambda x: f'<a href="{x}" target="_blank">{x}</a>'
)

# Rename columns and include HTML
display_df = paginated_df[columns_to_display].rename(columns=column_names)
display_df['Profile URL'] = paginated_df['Profile URL']

# Show table
st.markdown(f"### Showing users {start_idx + 1} to {min(end_idx, len(filtered_df))} of {len(filtered_df)} total")
st.markdown(display_df.to_html(escape=False, index=False), unsafe_allow_html=True)


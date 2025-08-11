import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# --- Step 1: Scrape Explore Agadir Souss Massa ---
@st.cache_data(show_spinner=True)
def scrape_explore_agadir():
    url = "https://explore-agadirsoussmassa.com/en/"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    attractions = []

    for link in soup.select('a[href*="/en/"]'):
        title = link.get_text(strip=True)
        href = link.get('href')
        if title and href and "en/" in href and len(title) > 3:
            attractions.append({
                "source": "Explore Agadir Souss Massa",
                "name": title,
                "url": href,
                "description": "",
                "category": ""
            })
    return attractions

# --- Step 2: Scrape Visit Agadir ---
@st.cache_data(show_spinner=True)
def scrape_visit_agadir():
    url = "https://visitagadir.com/"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    attractions = []

    for item in soup.select('a[href]'):
        title = item.get_text(strip=True)
        href = item.get('href')
        if title and href and "visitagadir.com" not in href and len(title) > 3:
            attractions.append({
                "source": "Visit Agadir",
                "name": title,
                "url": href,
                "description": "",
                "category": ""
            })
    return attractions

# --- Step 3: Merge & Remove Duplicates ---
@st.cache_data(show_spinner=True)
def get_attractions_df():
    explore_data = scrape_explore_agadir()
    visit_data = scrape_visit_agadir()
    df = pd.DataFrame(explore_data + visit_data).drop_duplicates(subset=["name"])
    return df

def main():
    st.title("Beyond the Map - Agadir Attractions Scraper")
    st.write(
        """
        This app scrapes tourist attractions from Explore Agadir Souss Massa and VisitAgadir.com.
        Use the filters below to explore the data.
        """
    )

    df = get_attractions_df()

    # Filters
    keyword = st.text_input("Filter by keyword in name:")
    category = st.text_input("Filter by category (not yet implemented):")
    min_len = st.slider("Minimum length of attraction name:", min_value=0, max_value=50, value=0)

    filtered = df.copy()
    if keyword:
        filtered = filtered[filtered['name'].str.contains(keyword, case=False, na=False)]
    if category:
        filtered = filtered[filtered['category'].str.contains(category, case=False, na=False)]
    if min_len > 0:
        filtered = filtered[filtered['name'].str.len() >= min_len]

    st.write(f"Showing {len(filtered)} attractions:")
    # Make URLs clickable in the dataframe display
    def make_clickable(url):
        return f"[Link]({url})"

    if not filtered.empty:
        filtered_display = filtered.copy()
        filtered_display['url'] = filtered_display['url'].apply(make_clickable)
        st.dataframe(filtered_display[['source', 'name', 'url']])
    else:
        st.write("No results match the filter criteria.")

    # Button to download CSV
    csv = filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download filtered data as CSV",
        data=csv,
        file_name='agadir_attractions_filtered.csv',
        mime='text/csv'
    )

if __name__ == "__main__":
    main()

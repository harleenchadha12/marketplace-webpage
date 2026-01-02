import streamlit as st
from snowflake_connector import SnowflakeConnector
import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import connection_snowflake
from streamlit_extras.app_logo import add_logo

st.set_page_config(page_icon="insights_logo_new_r.png", layout="wide")

st.markdown("""
    <style>
        div[data-testid="stSidebarHeader"] > img, div[data-testid="collapsedControl"] > img {
            height: 4rem;
            width: auto;
            margin-top : 1rem;
        }
        div[data-testid="stSidebarHeader"], div[data-testid="stSidebarHeader"] > *,
        div[data-testid="collapsedControl"], div[data-testid="collapsedControl"] > * {
            display: flex;
            align-items: center;
        }
    </style>
""", unsafe_allow_html=True)

st.logo("insights_logo_new_r.png")

# ---------- Load RSA Key ----------
key_path = os.path.join(os.path.dirname(__file__), '..', 'rsa_key.p8')

with open(key_path, "rb") as key:
    p_key = serialization.load_pem_private_key(
        key.read(),
        password='123'.encode(),
        backend=default_backend()
    )

    pkb = p_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

# ---------- Snowflake Connection ----------
conn_params = connection_snowflake.connection_snowflake()
connector = SnowflakeConnector(conn_params)
conn = connector.connect()

# ---------- Query Electric Vehicle Page ----------
query = """
SELECT PAGE_NAME, OVERVIEW, VIEWS_PUBLISHED, SOURCE_LINK, IMAGE_URLS
FROM WEBPAGE_DATA
WHERE PAGE_NAME = 'Electric Vehicles'
"""

cursor = conn.cursor()
cursor.execute(query)
df = cursor.fetch_pandas_all()

cursor.close()
conn.close()

# ---------- Render Page ----------
if not df.empty:
    page_name = df.iloc[0]['PAGE_NAME']
    page_overview = df.iloc[0]['OVERVIEW']
    views_published = df.iloc[0]['VIEWS_PUBLISHED']
    image_urls = df.iloc[0]['IMAGE_URLS']

    st.title(f"**{page_name}**")

    # Overview
    st.header("Overview")
    st.write(page_overview)

    # Views Published
    st.header("Views Published")
    sections = views_published.split("\n")
    for section in sections:
        if ':' in section:
            heading, description = section.split(":", 1)
            st.markdown(f"**{heading.strip()}**")
            st.write(description.strip())

    # Source Links
    st.header("Source Links")
    source_link = "https://developer.nrel.gov/docs/transportation/alt-fuel-stations-v1/"

    # Safe parsing of IMAGE_URLS
    if isinstance(image_urls, str):
        import ast
        try:
            # Try to convert stringified list to Python list
            parsed_urls = ast.literal_eval(image_urls)
            if isinstance(parsed_urls, str):
                image_urls = [parsed_urls]  # single string -> list
            elif isinstance(parsed_urls, list):
                image_urls = [url.strip() for url in parsed_urls if url.strip()]
            else:
                image_urls = []
        except:
            # If parsing fails, treat as single URL
            image_urls = [image_urls.strip()]

    if image_urls:
        st.markdown("""
            <style>
                .card {
                    border: 2px solid #ddd;
                    border-radius: 8px;
                    padding: 10px;
                    margin: 10px;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    width: 100%;
                    max-width: 250px;
                    height: 200px;
                    text-align: center;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                    transition: transform 0.3s ease-in-out;
                    flex-direction: column;
                }
                .card img {
                    width: 100%;
                    height: 100%;
                    object-fit: contain;
                    border-radius: 5px;
                }
                .card:hover {
                    transform: scale(1.05);
                    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4);
                }
            </style>
        """, unsafe_allow_html=True)

        # Use one column per image
        for img_url in image_urls:
            st.markdown(f"""
                <a href="{source_link}" target="_blank">
                    <div class="card">
                        <img src="{img_url}" alt="EV Image">
                    </div>
                </a>
            """, unsafe_allow_html=True)
    else:
        st.warning("No images available to display.")

else:
    st.warning("No data available for Electric Vehicle page.")


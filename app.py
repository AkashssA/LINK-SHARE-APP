import streamlit as st
from supabase import create_client, Client
import random, string

# Initialize Supabase
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# App Logic
st.set_page_config(page_title="QuickShare", page_icon="🔗")

# Check if someone visited a shared link (e.g., ?id=my-notes)
query_params = st.query_params
share_id = query_params.get("id")

if share_id:
    # --- VIEW MODE ---
    res = supabase.table("pastes").select("content").eq("slug", share_id).execute()
    if res.data:
        st.title("📄 Shared Content")
        st.code(res.data[0]['content'], language=None)
        if st.button("Create New Paste"):
            st.query_params.clear()
            st.rerun()
    else:
        st.error("Link not found!")
else:
    # --- CREATE MODE ---
    st.title("🔗 QuickShare")
    content = st.text_area("Paste content here...", height=300)
    custom_slug = st.text_input("Custom Link ID (Optional)")
    
    if st.button("Generate Shareable Link"):
        slug = custom_slug if custom_slug else ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        
        # Save to Supabase
        try:
            supabase.table("pastes").insert({"slug": slug, "content": content}).execute()
            full_url = f"https://your-app.streamlit.app/?id={slug}"
            st.success(f"Link created! Share this: {full_url}")
            st.code(full_url)
        except Exception as e:
            st.error("That ID is already taken! Try another one.")
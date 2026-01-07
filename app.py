import os
import streamlit as st
from supabase import create_client
import random
import string

# --- 1. CONNECTION LOGIC ---
@st.cache_resource
def init_connection():
    # Priority 1: Environment Variables (Docker)
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")

    # Priority 2: Streamlit Secrets (Cloud)
    if not url or not key:
        try:
            url = st.secrets.get("SUPABASE_URL")
            key = st.secrets.get("SUPABASE_KEY")
        except Exception:
            pass

    if not url or not key:
        st.error("❌ API Keys missing! Ensure SUPABASE_URL and SUPABASE_KEY are set.")
        st.stop()
        
    return create_client(url, key)

# Initialize Supabase
try:
    supabase = init_connection()
except Exception as e:
    st.error(f"Failed to connect to Supabase: {e}")
    st.stop()

# --- 2. UI CONFIG ---
st.set_page_config(page_title="QuickShare", page_icon="🔗")

# --- 3. APP LOGIC ---
query_params = st.query_params
share_id = query_params.get("id")

if share_id:
    # --- VIEW MODE ---
    res = supabase.table("pastes").select("content").eq("slug", share_id).execute()
    if res.data:
        st.title("📄 Shared Content")
        st.info(f"Viewing link ID: {share_id}")
        st.code(res.data[0]['content'], language=None)
        if st.button("⬅️ Create Your Own"):
            st.query_params.clear()
            st.rerun()
    else:
        st.error("🚫 Link not found! It may have been deleted or the ID is wrong.")
        if st.button("Go Home"):
            st.query_params.clear()
            st.rerun()
else:
    # --- CREATE MODE ---
    st.title("🔗 QuickShare")
    st.write("Paste your text or code below to generate a shareable URL.")

    content = st.text_area("Paste content here...", height=250, placeholder="Enter text here...")
    custom_slug = st.text_input("Custom ID (Optional)", placeholder="e.g., my-meeting-notes")
    
    if st.button("🚀 Generate Shareable Link", use_container_width=True):
        if content.strip():
            # Determine the Slug
            slug = custom_slug.strip() if custom_slug.strip() else ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            
           try:
                # Attempt to insert into Supabase
                response = supabase.table("pastes").insert({"slug": slug, "content": content}).execute()
                
                st.success("✅ Link Created Successfully!")
                
                # These three MUST align perfectly
                share_url = f"https://link-share-app-j41g.onrender.com/?id={slug}"
                st.subheader("Your Shareable Link:")
                st.code(share_url)
                st.balloons()
                
            except Exception as e:
                # Check if it's a unique constraint error
                if "duplicate key" in str(e).lower() or "already exists" in str(e).lower():
                    st.error(f"❌ The ID '{slug}' is already taken. Please try a different Custom ID or leave it blank for a random one.")
                else:
                    st.error("❌ An unexpected database error occurred.")
                    st.info(f"Debug Info: {e}")
        else:
            st.warning("⚠️ Please enter some content before generating a link.")

# --- FOOTER ---
st.divider()
st.caption("QuickShare AI Agent | Built with Streamlit & Supabase")

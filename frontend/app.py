import os
import requests
import streamlit as st

API_URL = os.environ.get("API_URL", "http://localhost:8080")

st.set_page_config(page_title="Node Registry", layout="wide")
st.title("Node Registry Dashboard")

# --- Health Status ---
st.subheader("API Health")
try:
    r = requests.get(f"{API_URL}/health", timeout=5)
    data = r.json()
    if data.get("status") == "ok":
        st.success(f"API online — DB: {data.get('db_status')} — Active nodes: {data.get('nodes_count')}")
    else:
        st.warning(f"API status: {data.get('status')}")
except Exception as e:
    st.error(f"Cannot reach API: {e}")

st.divider()

# --- Node List ---
st.subheader("Registered Nodes")
try:
    r = requests.get(f"{API_URL}/api/nodes", timeout=5)
    nodes = r.json()
    if nodes:
        st.dataframe(
            [{"name": n["name"], "host": n["host"], "port": n["port"], "status": n["status"]} for n in nodes],
            use_container_width=True,
        )
    else:
        st.info("No nodes registered yet.")
except Exception as e:
    st.error(f"Error fetching nodes: {e}")

st.divider()

# --- Register Node ---
st.subheader("Register Node")
with st.form("register_form"):
    name = st.text_input("Name")
    host = st.text_input("Host")
    port = st.number_input("Port", min_value=1, max_value=65535, value=8080)
    submitted = st.form_submit_button("Register")

if submitted:
    if not name or not host:
        st.error("Name and host are required.")
    else:
        try:
            r = requests.post(
                f"{API_URL}/api/nodes",
                json={"name": name, "host": host, "port": int(port)},
                timeout=5,
            )
            if r.status_code in (200, 201):
                st.success(f"Node '{name}' registered successfully.")
                st.rerun()
            else:
                st.error(f"Error {r.status_code}: {r.text}")
        except Exception as e:
            st.error(f"Request failed: {e}")

st.divider()

# --- Delete Node ---
st.subheader("Delete Node")
with st.form("delete_form"):
    del_name = st.text_input("Node name to delete")
    del_submitted = st.form_submit_button("Delete")

if del_submitted:
    if not del_name:
        st.error("Node name is required.")
    else:
        try:
            r = requests.delete(f"{API_URL}/api/nodes/{del_name}", timeout=5)
            if r.status_code == 200:
                st.success(f"Node '{del_name}' deleted.")
                st.rerun()
            else:
                st.error(f"Error {r.status_code}: {r.text}")
        except Exception as e:
            st.error(f"Request failed: {e}")

import streamlit as st
import hashlib
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import time

# ---------------------- FIREBASE INIT ----------------------
if not firebase_admin._apps:
    # Load the secrets dict
    firebase_config = st.secrets["firebase"]
    
    # Fix the private key line breaks
    firebase_config["private_key"] = firebase_config["private_key"].replace("\\n", "\n")
    
    # Create credentials and initialize app
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

# Get Firestore client
db = firestore.client()



# ---------------------- PASSWORD HASH ----------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ---------------------- FIRESTORE HELPERS ----------------------
def add_user(username, password, role="user"):
    ref = db.collection("users").document(username)
    if ref.get().exists:
        return False, "Username already exists."
    ref.set({"password": hash_password(password), "role": role})
    return True, "Account created."

def verify_user(username, password):
    ref = db.collection("users").document(username).get()
    if not ref.exists:
        return False, None
    data = ref.to_dict()
    if data["password"] != hash_password(password):
        return False, None
    banned = db.collection("banned").document(username).get()
    if banned.exists:
        return False, "banned"
    return True, data["role"]

def ban_user(username):
    db.collection("banned").document(username).set({"banned": True})

def unban_user(username):
    db.collection("banned").document(username).delete()

def add_message(username, role, content):
    db.collection("messages").add({
        "author": username,
        "role": role,
        "content": content,
        "timestamp": firestore.SERVER_TIMESTAMP
    })

def get_messages():
    docs = db.collection("messages").order_by("timestamp").stream()
    return [d.to_dict() for d in docs]

# ---------------------- STREAMLIT CONFIG ----------------------
st.set_page_config(page_title="Chat App", layout="wide",page_icon="💬")


hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# ---------------------- LOGIN ----------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["Login 🔑", "Sign Up 📝"])

    with tab1:
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        if st.button("Log In"):
            ok, role = verify_user(username, password)
            if ok:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = role
                st.rerun()
            else:
                st.error("Invalid login or banned.")

    with tab2:
        new_user = st.text_input("Create username", placeholder="Pick a username")
        new_pass = st.text_input("Create password", type="password", placeholder="Pick a secure password")
        if st.button("Create Account"):
            ok, msg = add_user(new_user, new_pass)
            if ok:
                st.success(msg)
            else:
                st.error(msg)

    st.stop()

# ---------------------- SIDEBAR ----------------------
st.sidebar.header("👥 Users")
users = db.collection("users").stream()
banned = {d.id for d in db.collection("banned").stream()}

for u in users:
    name = u.id
    role = u.to_dict().get("role", "user")

    color = "red" if role == "admin" else "lightgreen"
    banned_tag = " (banned)" if name in banned else ""
    role_tag_side = "(Admin)" if role == "admin" else ""

    col = st.sidebar.container()
   

    col.markdown(f"<b style='color:{color}; font-weight:bold;'>{name}{role_tag_side}{banned_tag}</b>", unsafe_allow_html=True)

    if st.session_state.role == "admin" and name != st.session_state.username:
        c1, c2 = col.columns(2)
        if name not in banned:
            if c2.button("ban", key=f"ban_{name}"):
                ban_user(name)
                time.sleep(0.2)
                st.rerun()
        else:
            if c2.button("unnban", key=f"unban_{name}"):
                unban_user(name)
                time.sleep(0.2)
                st.rerun()



# ---------------------- MODERN CHAT UI ----------------------
left, right = st.columns([4, 1])

with left:
    st.subheader("💬 Chat Room")

    chat_html = "<div style='height:500px; overflow-y:auto; padding:10px; background:#1e1e2f; border-radius:12px;'>"
    msgs = get_messages()
    for m in msgs:
        author = m.get("author", "?")
        role = m.get("role", "user")
        text = m.get("content", "")
        ts = m.get("timestamp")
        if ts:
            ts_str = ts.strftime('%H:%M:%S') if isinstance(ts, datetime) else str(ts)
        else:
            ts_str = ''
        role_tag = "(Admin)" if role == "admin" else "(User)"
        color = "#ff4d4d" if role == "admin" else "#ffd966"
        chat_html += f"<div style='padding:5px; margin-bottom:6px; border-radius:6px; display:flex; justify-content:space-between;'>"
        chat_html += f"<span><b style='color:{color};'>{author}</b> {role_tag}</span>"
        chat_html += f"<span style='color:#888;'>{ts_str}</span>"
        chat_html += f"</div><div style='padding-left:10px; color:#fafafa;'>{text}</div>"
    chat_html += "</div>"

    st.markdown(chat_html, unsafe_allow_html=True)

    msg = st.chat_input("Type a message...")
    if msg:
        add_message(st.session_state.username, st.session_state.role, msg)
        time.sleep(0.1)
        st.rerun()

with right:
    if st.session_state.role != "admin":
        st.write("User name: ", st.session_state.username)

    else:
        st.subheader("⚙️ Admin Tools")
        st.write("User name: ", st.session_state.username)
        if st.button("🗑 Clear Chat"):
            for doc in db.collection("messages").stream():
                doc.reference.delete()
            st.success("Chat cleared.")
            time.sleep(0.1)
            st.rerun()
    if st.button("🚪 Log Out"):
        st.session_state.logged_in = False
        st.rerun() 
    st.write("> For any issues, contact the admin. ")
    st.write("> More features coming soon... ")         



st.markdown(
    """
    <style>
        .social-icons {
            text-align: center;
            margin-top: 60px;
        }

        .social-icons a {
            text-decoration: none !important;
            margin: 0 20px;
            font-size: 28px;
            display: inline-block;
            color: inherit !important; /* force child i to use its color */
        }

        

        /* Hover glitch animation */
        .social-icons a:hover {
            animation: glitch 0.3s infinite;
        }

        
        /* Contact us heading */
        .contact-heading {
            text-align: center;
            font-size: 25px;
            font-weight: bold;
            margin-bottom: 15px;
        }
        @keyframes glitch {
            0% { transform: translate(0px, 0px); text-shadow: 2px 2px #0ff, -2px -2px #f0f; }
            20% { transform: translate(-2px, 1px); text-shadow: -2px 2px #0ff, 2px -2px #f0f; }
            40% { transform: translate(2px, -1px); text-shadow: 2px -2px #0ff, -2px 2px #f0f; }
            60% { transform: translate(-1px, 2px); text-shadow: -2px 2px #0ff, 2px -2px #f0f; }
            80% { transform: translate(1px, -2px); text-shadow: 2px -2px #0ff, -2px 2px #f0f; }
            100% { transform: translate(0px, 0px); text-shadow: 2px 2px #0ff, -2px -2px #f0f; }
        }
    </style>
    <div class="social-icons">
    <div class="contact-heading">Contact Us:</div>
        <a class='fb' href='https://www.facebook.com/sakibhossain.tahmid' target='_blank'>
            <i class='fab fa-facebook'></i> 
        </a> 
        <a class='insta' href='https://www.instagram.com/_sakib_000001' target='_blank'>
            <i class='fab fa-instagram'></i> 
        </a> 
        <a class='github' href='https://github.com/sakib-12345' target='_blank'>
            <i class='fab fa-github'></i> 
        </a> 
        <a class='email' href='mailto:sakibhossaintahmid@gmail.com'>
            <i class='fas fa-envelope'></i> 
        </a>
    </div>
    
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    """,
    unsafe_allow_html=True
)


st.markdown(
            f'<div style="text-align: center; color: grey;">&copy; 2025 Sakib Hossain Tahmid. All Rights Reserved.</div>',
            unsafe_allow_html=True
           ) 





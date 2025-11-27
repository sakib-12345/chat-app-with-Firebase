
# 💬 Chat App
Author: Sakib Hossain Tahmid
* Try my App [Click Here](https://chat-firebase.streamlit.app/)
<p align="center">
  <img src="https://github.com/sakib-12345/chat-app-with-Firebase/blob/main/App_icon.png" alt="Screenshot" width="200">
</p>

* A simple real-time chat web app built with **Python** and **Streamlit**, using **Firebase** as the datastore. Users can sign up, log in, chat with others, and admins can ban users and clear messages.

## 🚀 Features

### 👤 User Features
- Sign up & log in  
- Send and receive messages  
- Chat with multiple users  
- Auto-refresh chat feed  

### 🛡️ Admin Features
- Ban & unban users  
- Clear full chat history  
- View all users  
- Manage messages  
### 🔑 Security Features
-  Fully encrypted password in Database
-  You can also make the chat encrypted (with python **hash** library)
-  Even database admin can't see passwords
## 🛠️ Tech Stack
- **Python**
- **Streamlit**
- **Firebase**
## 📊 Database Setup
- Step-1: *Create a database in Firebase(BY GOOGLE)*
- Step-2: *Copy the api file and make it like Toml format(Don't share with anyone and keep it secret)*
- Step-3: *Use it as env. varible file*
- Step-4: *Deploy it in any python server*
  
<br>***"IN MY CASE, I USE STREAMLIT FREE SERVER AND PASTE THE API KEY IN STREAMLIT SECRETS."***


## 🔧 Setup(Local)

#### 1.Clone
```bash
https://github.com/sakib-12345/chat-app-with-Firebase.git
```
#### 2.Open folder
```bash
cd chat-app-with-Firebase
```
#### 3.Install Libraries
```bash
pip install -r requirements.txt
```
#### 4.Run it (Locally)
```bash
streamlit run chat.py
```
## License
- This project is licensed under the MIT License. You can use, copy, and modify it freely as long as you include the original license.

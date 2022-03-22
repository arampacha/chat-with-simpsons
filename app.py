import os
import streamlit as st
import json
import requests

import time

API_TOKEN = os.environ.get("HF_API_TOKEN")
headers = {"Authorization": f"Bearer {API_TOKEN}"}
API_URL = "https://api-inference.huggingface.co/models/arampacha/DialoGPT-medium-simpsons"


def query(payload):
    data = json.dumps(payload)
    response = requests.request("POST", API_URL, headers=headers, data=data)
    return json.loads(response.content.decode("utf-8"))

def fake_query(payload):
    user_input = payload["inputs"]["text"]
    time.sleep(1)
    res = {
        "generated_text": user_input[::-1],
        "conversation":{
            "past_user_inputs": st.session_state.past_user_inputs + [user_input],
            "generated_responses": st.session_state.generated_responses + [user_input[::-1]],
        },
    }
    return res

parameters = {
    "min_length":None,
    "max_length":100,
    "top_p":0.92,
    "temperature":1.0,
    "repetition_penalty":None,
}
options = {
    "use_cache":False,
    "wait_for_model":False
}

def on_input():
    
    if st.session_state.count > 0:
        user_input = st.session_state.user_input
        st.session_state.full_text += f"_User_  >>> {user_input}\n\n"
        dialog_output.markdown(st.session_state.full_text)
        st.session_state.user_input = ""

        payload = {
            "inputs": {
                "text": user_input,
                "past_user_inputs": st.session_state.past_user_inputs,
                "generated_responses": st.session_state.generated_responses,
            },
            "parameters": parameters,
            "options":options,
        }
        # result = fake_query(payload)
        result = query(payload)
        try:
            st.session_state.update(result["conversation"])
            st.session_state.full_text += f'_Chatbot_ > {result["generated_text"]}\n\n'
        except:
            st.write("D'oh! Something went wrong. Try to rerun the app.")
            st.write(result)
    st.session_state.count += 1



# init session state
if "past_user_inputs" not in st.session_state:
    st.session_state["past_user_inputs"] = []
if "generated_responses" not in st.session_state:
    st.session_state["generated_responses"] = []
if "full_text" not in st.session_state:
    st.session_state["full_text"] = ""
if "user_input" not in st.session_state:
    st.session_state["user_input"] = ""
if "count" not in st.session_state:
    st.session_state["count"] = 0

# body
st.title("Chat with Simpsons")

st.image(
    "https://raw.githubusercontent.com/arampacha/chat-with-simpsons/main/the-simpsons.png",
    caption="(c) 20th Century Fox Television",
)
if st.session_state.count == 0:
    st.write("Start dialog by inputing some text:")

dialog_output = st.empty()

if st.session_state.count > 0:
    dialog_output.markdown(st.session_state.full_text)

user_input = st.text_input(
    "> User: ",
    # value="Hey Homer! How is it going?",
    on_change=on_input(),
    key="user_input",
)

dialog_text = st.session_state.full_text
dialog_output.markdown(dialog_text)

def restart():
    st.session_state.clear()
    
st.button("Restart", on_click=st.session_state.clear)
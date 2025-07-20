import streamlit as st
import torch
from transformers import AutoModel, AutoTokenizer,AutoModelForCausalLM
from transformers.generation import GenerationConfig
import json
from openai import OpenAI

openai_api_key = "ANY THING"
openai_api_base = "http://xunziallm.njau.edu.cn:21180/v1"
# 设置页面标题、图标和布局
st.set_page_config(
    page_title="荀子大模型效果演示",
    page_icon=":robot:",
    layout="wide"
)
# 在sider添加图片
from PIL import Image
image = Image.open('荀子logonew.png')
st.sidebar.image(image, width=300)

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)
if "history" not in st.session_state:
    st.session_state.history = []
if "past_key_values" not in st.session_state:
    st.session_state.past_key_values = None
# 设置max_length、top_p和temperature
max_new_tokens = st.sidebar.slider("max_new_tokens", 0, 2048, 1024, step=1)
top_p = st.sidebar.slider("top_p", 0.0, 1.0, 0.8, step=0.01)
temperature = st.sidebar.slider("temperature", 0.0, 1.0, 0.9, step=0.01)



# 清理会话历史
    
buttonClean = st.sidebar.button("清理会话历史", key="clean")
if buttonClean:
    st.session_state.history = []
    st.session_state.past_key_values = None
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    st.rerun()

for i, message in enumerate(st.session_state.history):
    if message["role"] == "user":
        with st.chat_message(name="user", avatar="用户头像.png"):
            st.markdown(message["content"])
    else:
        with st.chat_message(name="assistant", avatar="机器人头像.png"):
            st.markdown(message["content"])

# 输入框和输出框
with st.chat_message(name="user", avatar="用户头像.png"):
    input_placeholder = st.empty()
with st.chat_message(name="assistant", avatar="机器人头像.png"):
    message_placeholder = st.empty()

# 获取用户输入
prompt_text = st.chat_input("请输入您的问题")

def json2tuple(json_list):
    tuple_list = []
    for i in range(0, len(json_list) - 1, 2):
        if json_list[i]['role'] == 'user' and json_list[i+1]['role'] == 'assistant':
            tuple_list.append((json_list[i]['content'], json_list[i+1]['content']))
    return tuple_list


# 对话部分
if prompt_text:
    need=[]
    input_placeholder.markdown(prompt_text)
    history = st.session_state.history
    if not history:
        history.append({"role": "system", "content": "You are a helpful assistant."})
    history_=json2tuple(history)
    history.append({"role":"user","content":prompt_text})
    past_key_values = st.session_state.past_key_values
    #获取流式输出
    response = client.chat.completions.create(
        model="/home/gpu0/Xunzi-Qwen1.5-7B_chat",
        messages=history,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_new_tokens,
        stream=True)
    xuanran=''    
    for chunk in response:
        token=chunk.choices[0].delta.content
        if token is not None:
            xuanran+=str(chunk.choices[0].delta.content)
            message_placeholder.markdown(xuanran)
            need.append(chunk.choices[0].delta.content)
    responses=''.join(need)
    history.append({"role":"assistant","content":responses})
    print(history)

    # 更新历史记录和past key values
    st.session_state.history = history
    st.session_state.past_key_values = past_key_values
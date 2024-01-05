import streamlit as st
import pandas as pd

st.title("hello world")
x = 10
x

df = pd.DataFrame({'col1': [1,2,3]})
df

uploaded_file = st.file_uploader("ログをアップロードしてください。")

st.balloons()
st.snow()

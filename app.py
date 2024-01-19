import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from io import StringIO

st.title("hello world")
x = 10
x

df = pd.DataFrame({'col1': [1,2,3]})
df

# 対象データをリスト化
def get_piyolog_all_items(data):
    all_items = []

    # for month_text in month_texts:
    # 改行で分割
    lines = data.splitlines()
    array = np.array(lines)

    day = ''
    for index, item in enumerate(array):

        # 日付取得（月次データ）
        if item == '----------' and index < len(array) - 1:
            day = array[index + 1][:-3] # 曜日「（月）など」の末尾3文字を除く文字列を抽出
            day_date = datetime.datetime.strptime(day, '%Y/%m/%d').strftime("%-d")

        # 対象項目の場合
        if item != '' and check_item(item):
            # 空白で分割
            record = item.split()

            record_dt = datetime.datetime.strptime(day + ' ' + record[0], '%Y/%m/%d %H:%M')
            record_type = None
            record_subtype = record[1]
            record_value = None
            record_timespan = None

            if '寝る' in record_subtype:
                record_type = '睡眠'

            if '起きる' in record_subtype:
                record_type = '睡眠'

            if 'ミルク' in record_subtype or '搾母乳' in record_subtype:
                record_type = '食事'
                # 搾母乳も項目名はミルクにする
                record_subtype = 'ミルク'
                # 時間は10分固定にする
                record_timespan = 10
                # ミルク量
                record_value = int(record[2].replace('ml', ''))

            if '母乳' in record_subtype:
                record_type = '食事'
                record_time = 0
                # 授乳時間の合計を計算する
                for r in record[2:]:
                    if '分' in r:
                        record_time += int(re.sub(r'左|右|分', '', r, 2)) # 「左」や「右」などの先頭1文字と「分」の末尾1文字を除外
                record_timespan = record_time
                        
            # 記録
            all_items.append([day_date, record_dt, record_type, record_subtype, record_value])

    return all_items

# 対象項目
def check_item(text):
    if re.findall('起きる|寝る|母乳|ミルク|離乳食|搾母乳', text) and re.match(r'([01][0-9]|2[0-3]):[0-5][0-9]', text):
        return True
    return False

uploaded_file = st.file_uploader("ログをアップロードしてください。")
if uploaded_file is not None:
    st.balloons()
    
    # To convert to a string based IO:
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    # stringio = open("sample_file.txt", "r", encoding="utf-8")  # ローカルのサンプルファイル

    # To read file as string:
    string_data = stringio.read()
    # st.markdown('### アップロードファイル（先頭1000文字）')
    # st.write(string_data[:1000])

    df = pd.DataFrame(get_piyolog_all_items(string_data),columns=['日付','日時','分類','項目','ミルク量'])
    st.markdown('### アップロードファイル')
    df

    # meal_data = df[df['分類'] == '食事']

    st.markdown('### 日付ごとのミルク量の推移')  # （日付ごとにグルーピングして棒グラフにしたい）
    # グラフの描画
    fig, ax = plt.subplots()
    ax.plot(df['日付'], df['ミルク量'], marker='o')
    ax.set_title('Milk Volume Over Time')
    ax.set_xlabel('date')
    ax.set_ylabel('milk(ml)')
    st.pyplot(fig)

    st.markdown('### 時間帯とミルク量のヒートマップ')
    # グラフの描画
    meal_data = df[df['分類'] == '食事']
    df['Hour'] = pd.to_datetime(meal_data['日時']).dt.hour
    # ミルク量の範囲を定義
    bins = [100, 120, 140, 160, 180, 200, float('inf')]
    labels = ['100-119', '120-139', '140-159', '160-179', '180-199', '200+']
    df['Amount Range'] = pd.cut(df['ミルク量'], bins=bins, labels=labels, right=False)
    # 集計
    heatmap_data = df.groupby(['Amount Range', 'Hour']).size().unstack().fillna(0)
    # ヒートマップの作成
    fig, ax = plt.subplots()
    sns.heatmap(heatmap_data, annot=True, cmap='coolwarm', ax=ax)
    ax.set_title('Heatmap of Milk Consumption by Hour and Amount Range')
    ax.set_ylabel('Milk Amount Range')
    ax.set_xlabel('Hour of Day')
    st.pyplot(fig)

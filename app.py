import streamlit as st
import pandas as pd
import numpy as np
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
            day_date = datetime.datetime.strptime(day, '%Y/%m/%d')

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
            all_items.append([day_date, record_dt, record_type, record_subtype, record_timespan, record_value])

    return all_items

# 対象項目
def check_item(text):
    if re.findall('起きる|寝る|母乳|ミルク|離乳食|搾母乳', text) and re.match(r'([01][0-9]|2[0-3]):[0-5][0-9]', text):
        return True
    return False

CN_DATE = 'date' # 日付
CN_NAP_COUNT = 'nap_count' # 昼寝回数
CN_NAP_MINUTE = 'nap_minute' # 昼寝時間
CN_NIGHT_SLEEP_COUNT = 'night_sleep_count' # 夜寝回数
CN_NIGHT_SLEEP_MINUTE = 'night_sleep_minute' # 夜寝時間
CN_NIGHT_WAKEUP_COUNT = 'night_wakeup_count' # 夜に起きる回数
CN_NIGHT_WAKEUP_MINUTE = 'night_wakeup_minute' # 夜に起きている時間
CN_MILK_COUNT = 'milk_count' # ミルク回数
CN_MILK_ML = 'milk_ml' # ミルク量
CN_BREASTFEEDING_COUNT  = 'breastfeeding_count' # 授乳回数
CN_BREASTFEEDING_MINUTE = 'breastfeeding_minute' # 授乳時間
CN_BABY_FOOD_COUNT = 'baby_food_count' # 離乳食回数
CN_BABY_FOOD_MINUTE = 'baby_food_minute' # 離乳食時間
CN_AGE_OF_MONTH = 'age_of_month' # 月齢


uploaded_file = st.file_uploader("ログをアップロードしてください。")
if uploaded_file is not None:
    st.balloons()
    st.snow()
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()

    # To convert to a string based IO:
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    
    # To read file as string:
    string_data = stringio.read()
    st.markdown('### アップロードファイル（先頭1000文字）')
    st.write(string_data[:1000])
    
    df = pd.DataFrame(get_piyolog_all_items(string_data),columns=[CN_DATE, '日時','分類','項目','時間','ミルク量'])
    st.markdown('### アップロードファイル(dataframe）')
    df
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# 設定網頁標題與寬度
st.set_page_config(
    page_title="龍天宮歷年活動報名人數系統", page_icon="🏮", layout="wide"
)

st.title("🏮 龍天宮歷年活動報名人數統計與分佈系統")
st.markdown("請透過左側或下方標籤選擇對應的活動項目進行資料填寫與報名趨勢分析。")

# 初始化 Session State 以保存各組資料（避免重新整理後資料消失）
if "data_jg" not in st.session_state:
    st.session_state.data_jg = pd.DataFrame(
        {"年份": [2024, 2025, 2026], "祭改人數": [120, 140, 150]}
    )

if "data_light" not in st.session_state:
    st.session_state.data_light = pd.DataFrame(
        {
            "年份": [2024, 2025, 2026],
            "300元光明燈": [200, 220, 250],
            "500元光明燈": [40, 45, 50],
            "300元太歲": [120, 135, 150],
            "500元太歲": [10, 12, 15],
        }
    )

if "data_dou" not in st.session_state:
    st.session_state.data_dou = pd.DataFrame(
        {
            "年份": [2024, 2025, 2026],
            "1000元年斗": [40, 45, 50],
            "3000元年斗": [8, 9, 10],
            "5000元年斗": [15, 18, 20],
            "6000元年斗": [10, 12, 15],
        }
    )

if "data_march" not in st.session_state:
    st.session_state.data_march = pd.DataFrame(
        {"年份": [2024, 2025, 2026], "全家補運人數": [130, 140, 150], "補財庫人數": [80, 90, 100]}
    )

if "data_personal" not in st.session_state:
    st.session_state.data_personal = pd.DataFrame(
        {
            "年份": [2024, 2025, 2026],
            "補運月份": ["六月補運", "九月補運", "六月補運"],
            "補運人數": [120, 135, 150],
            "補財庫月份": ["六月補運", "九月補運", "六月補運"],
            "補財庫人數": [85, 95, 100],
        }
    )

# 建立五大功能分頁
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "1. 正月祭改",
        "2. 正月光明燈及太歲",
        "3. 正月年斗",
        "4. 三月全家補運及補財庫",
        "5. 個人補運及補財庫",
    ]
)

# ==================== 1. 正月祭改 ====================
with tab1:
  st.header("✨ 正月祭改報名管理")

  with st.form("form_jg"):
    col1, col2 = st.columns(2)
    with col1:
      year_jg = st.number_input(
          "年份", min_value=2000, max_value=2100, value=2027, step=1, key="y_jg"
      )
    with col2:
      count_jg = st.number_input(
          "祭改人數", min_value=0, value=160, step=1, key="c_jg"
      )

    submitted_jg = st.form_submit_button("新增 / 更新祭改資料")
    if submitted_jg:
      # 若年份已存在則更新，否則新增
      if year_jg in st.session_state.data_jg["年份"].values:
        st.session_state.data_jg.loc[
            st.session_state.data_jg["年份"] == year_jg, "祭改人數"
        ] = count_jg
      else:
        new_row = pd.DataFrame({"年份": [year_jg], "祭改人數": [count_jg]})
        st.session_state.data_jg = pd.concat(
            [st.session_state.data_jg, new_row], ignore_index=True
        )
      st.session_state.data_jg = st.session_state.data_jg.sort_values(
          "年份"
      ).reset_index(drop=True)
      st.success(f"成功儲存 {year_jg} 年正月祭改資料！")

  st.subheader("📊 正月祭改報名人數總覽表")
  st.dataframe(st.session_state.data_jg, use_container_width=True)

  # 畫曲線圖
  df_jg = st.session_state.data_jg
  fig_jg = go.Figure()
  fig_jg.add_trace(
      go.Scatter(
          x=df_jg["年份"],
          y=df_jg["祭改人數"],
          mode="lines+markers",
          name="祭改人數",
          line=dict(color="firebrick", width=3),
      )
  )
  fig_jg.update_layout(
      title="正月祭改報名人數分佈圖",
      xaxis_title="年份祭改",
      yaxis_title="祭改人數",
      template="plotly_white",
  )
  st.plotly_chart(fig_jg, use_container_width=True)

# ==================== 2. 正月光明燈及太歲 ====================
with tab2:
  st.header("🏮 正月光明燈及太歲報名管理")

  with st.form("form_light"):
    col1, col2, col3 = st.columns(3)
    with col1:
      year_light = st.number_input(
          "年份", min_value=2000, max_value=2100, value=2027, step=1, key="y_li"
      )
    with col2:
      st.markdown("**光明燈設定**")
      light_type = st.selectbox(
          "選擇光明燈方案", ["300元光明燈", "500元光明燈"]
      )
      count_light_300 = st.number_input("300元光明燈人數", min_value=0, value=260)
      count_light_500 = st.number_input("500元光明燈人數", min_value=0, value=55)
    with col3:
      st.markdown("**太歲設定**")
      taisu_type = st.selectbox("選擇太歲方案", ["300元太歲", "500元太歲"])
      count_taisu_300 = st.number_input("300元太歲人數", min_value=0, value=160)
      count_taisu_500 = st.number_input("500元太歲人數", min_value=0, value=18)

    submitted_light = st.form_submit_button("新增 / 更新光明燈與太歲資料")
    if submitted_light:
      df_l = st.session_state.data_light
      if year_light in df_l["年份"].values:
        df_l.loc[df_l["年份"] == year_light, "300元光明燈"] = count_light_300
        df_l.loc[df_l["年份"] == year_light, "500元光明燈"] = count_light_500
        df_l.loc[df_l["年份"] == year_light, "300元太歲"] = count_taisu_300
        df_l.loc[df_l["年份"] == year_light, "500元太歲"] = count_taisu_500
      else:
        new_row = pd.DataFrame({
            "年份": [year_light],
            "300元光明燈": [count_light_300],
            "500元光明燈": [count_light_500],
            "300元太歲": [count_taisu_300],
            "500元太歲": [count_taisu_500],
        })
        st.session_state.data_light = pd.concat(
            [df_l, new_row], ignore_index=True
        )
      st.session_state.data_light = st.session_state.data_light.sort_values(
          "年份"
      ).reset_index(drop=True)
      st.success(f"成功儲存 {year_light} 年光明燈與太歲資料！")

  st.subheader("📊 光明燈及太歲報名人數總覽表")
  st.dataframe(st.session_state.data_light, use_container_width=True)

  df_light = st.session_state.data_light

  # 圖表 1：光明燈雙Y軸曲線圖
  fig_light = make_subplots(specs=[[{"secondary_y": True}]])
  fig_light.add_trace(
      go.Scatter(
          x=df_light["年份"],
          y=df_light["300元光明燈"],
          name="300元光明燈人數",
          line=dict(color="orange", width=3),
      ),
      secondary_y=False,
  )
  fig_light.add_trace(
      go.Scatter(
          x=df_light["年份"],
          y=df_light["500元光明燈"],
          name="500元光明燈人數",
          line=dict(color="orangered", width=3, dash="dash"),
      ),
      secondary_y=True,
  )
  fig_light.update_layout(
      title="正月光明燈報名人數分佈圖", xaxis_title="年份光明燈", template="plotly_white"
  )
  fig_light.update_yaxes(title_text="<b>300元光明燈人數</b>", secondary_y=False)
  fig_light.update_yaxes(title_text="<b>500元光明燈人數</b>", secondary_y=True)
  st.plotly_chart(fig_light, use_container_width=True)

  # 圖表 2：太歲雙Y軸曲線圖
  fig_taisu = make_subplots(specs=[[{"secondary_y": True}]])
  fig_taisu.add_trace(
      go.Scatter(
          x=df_light["年份"],
          y=df_light["300元太歲"],
          name="300元太歲人數",
          line=dict(color="dodgerblue", width=3),
      ),
      secondary_y=False,
  )
  fig_taisu.add_trace(
      go.Scatter(
          x=df_light["年份"],
          y=df_light["500元太歲"],
          name="500元太歲人數",
          line=dict(color="darkblue", width=3, dash="dash"),
      ),
      secondary_y=True,
  )
  fig_taisu.update_layout(
      title="正月太歲報名人數分佈圖", xaxis_title="年份太歲", template="plotly_white"
  )
  fig_taisu.update_yaxes(title_text="<b>300元太歲人數</b>", secondary_y=False)
  fig_taisu.update_yaxes(title_text="<b>500元太歲人數</b>", secondary_y=True)
  st.plotly_chart(fig_taisu, use_container_width=True)

# ==================== 3. 正月年斗 ====================
with tab3:
  st.header("⭐ 正月年斗報名管理")

  with st.form("form_dou"):
    col1, col2 = st.columns(2)
    with col1:
      year_dou = st.number_input(
          "年份", min_value=2000, max_value=2100, value=2027, step=1, key="y_do"
      )
      dou_type = st.selectbox(
          "年斗方案選項",
          ["1000元年斗", "3000元年斗", "5000元年斗", "6000元年斗"],
      )
    with col2:
      c_1k = st.number_input("1000元年斗人數", min_value=0, value=55)
      c_3k = st.number_input("3000元年斗人數", min_value=0, value=12)
      c_5k = st.number_input("5000元年斗人數", min_value=0, value=22)
      c_6k = st.number_input("6000元年斗人數", min_value=0, value=16)

    submitted_dou = st.form_submit_button("新增 / 更新年斗資料")
    if submitted_dou:
      df_d = st.session_state.data_dou
      if year_dou in df_d["年份"].values:
        df_d.loc[df_d["年份"] == year_dou, "1000元年斗"] = c_1k
        df_d.loc[df_d["年份"] == year_dou, "3000元年斗"] = c_3k
        df_d.loc[df_d["年份"] == year_dou, "5000元年斗"] = c_5k
        df_d.loc[df_d["年份"] == year_dou, "6000元年斗"] = c_6k
      else:
        new_row = pd.DataFrame({
            "年份": [year_dou],
            "1000元年斗": [c_1k],
            "3000元年斗": [c_3k],
            "5000元年斗": [c_5k],
            "6000元年斗": [c_6k],
        })
        st.session_state.data_dou = pd.concat(
            [df_d, new_row], ignore_index=True
        )
      st.session_state.data_dou = st.session_state.data_dou.sort_values(
          "年份"
      ).reset_index(drop=True)
      st.success(f"成功儲存 {year_dou} 年年斗資料！")

  st.subheader("📊 年斗報名人數總覽表")
  st.dataframe(st.session_state.data_dou, use_container_width=True)

  df_dou = st.session_state.data_dou
  fig_dou = go.Figure()
  fig_dou.add_trace(
      go.Scatter(
          x=df_dou["年份"],
          y=df_dou["1000元年斗"],
          name="1000元",
          mode="lines+markers",
      )
  )
  fig_dou.add_trace(
      go.Scatter(
          x=df_dou["年份"],
          y=df_dou["3000元年斗"],
          name="3000元",
          mode="lines+markers",
      )
  )
  fig_dou.add_trace(
      go.Scatter(
          x=df_dou["年份"],
          y=df_dou["5000元年斗"],
          name="5000元",
          mode="lines+markers",
      )
  )
  fig_dou.add_trace(
      go.Scatter(
          x=df_dou["年份"],
          y=df_dou["6000元年斗"],
          name="6000元",
          mode="lines+markers",
      )
  )

  fig_dou.update_layout(
      title="正月年斗報名人數分佈圖",
      xaxis_title="年份年斗",
      yaxis_title="年斗人數",
      template="plotly_white",
  )
  st.plotly_chart(fig_dou, use_container_width=True)

# ==================== 4. 三月全家補運及補財庫 ====================
with tab4:
  st.header("💰 三月全家補運及補財庫報名管理")

  with st.form("form_march"):
    col1, col2, col3 = st.columns(3)
    with col1:
      year_m = st.number_input(
          "年份", min_value=2000, max_value=2100, value=2027, step=1, key="y_ma"
      )
    with col2:
      count_m_fortune = st.number_input(
          "全家補運人數", min_value=0, value=160, step=1
      )
    with col3:
      count_m_wealth = st.number_input(
          "補財庫人數", min_value=0, value=110, step=1
      )

    submitted_m = st.form_submit_button("新增 / 更新三月補運資料")
    if submitted_m:
      df_m = st.session_state.data_march
      if year_m in df_m["年份"].values:
        df_m.loc[df_m["年份"] == year_m, "全家補運人數"] = count_m_fortune
        df_m.loc[df_m["年份"] == year_m, "補財庫人數"] = count_m_wealth
      else:
        new_row = pd.DataFrame({
            "年份": [year_m],
            "全家補運人數": [count_m_fortune],
            "補財庫人數": [count_m_wealth],
        })
        st.session_state.data_march = pd.concat(
            [df_m, new_row], ignore_index=True
        )
      st.session_state.data_march = st.session_state.data_march.sort_values(
          "年份"
      ).reset_index(drop=True)
      st.success(f"成功儲存 {year_m} 年三月全家補運及補財庫資料！")

  st.subheader("📊 三月全家補運及補財庫報名人數總覽表")
  st.dataframe(st.session_state.data_march, use_container_width=True)

  df_march = st.session_state.data_march
  fig_march = make_subplots(specs=[[{"secondary_y": True}]])
  fig_march.add_trace(
      go.Scatter(
          x=df_march["年份"],
          y=df_march["全家補運人數"],
          name="全家補運人數",
          line=dict(color="green", width=3),
      ),
      secondary_y=False,
  )
  fig_march.add_trace(
      go.Scatter(
          x=df_march["年份"],
          y=df_march["補財庫人數"],
          name="補財庫人數",
          line=dict(color="goldenrod", width=3, dash="dash"),
      ),
      secondary_y=True,
  )
  fig_march.update_layout(
      title="三月全家補運及補財庫報名人數分佈圖",
      xaxis_title="年份全家補運",
      template="plotly_white",
  )
  fig_march.update_yaxes(title_text="<b>全家補運人數</b>", secondary_y=False)
  fig_march.update_yaxes(title_text="<b>補財庫人數</b>", secondary_y=True)
  st.plotly_chart(fig_march, use_container_width=True)

# ==================== 5. 個人補運及補財庫 ====================
with tab5:
  st.header("🧧 個人補運及補財庫報名管理")

  with st.form("form_personal"):
    col1, col2, col3 = st.columns(3)
    with col1:
      year_p = st.number_input(
          "年份", min_value=2000, max_value=2100, value=2027, step=1, key="y_pe"
      )
    with col2:
      st.markdown("**補運設定**")
      p_fortune_month = st.selectbox("補運下拉選單", ["六月補運", "九月補運"])
      p_fortune_count = st.number_input("補運人數", min_value=0, value=160)
    with col3:
      st.markdown("**補財庫設定**")
      p_wealth_month = st.selectbox("補財庫下拉選單", ["六月補運", "九月補運"])
      p_wealth_count = st.number_input("補財庫人數", min_value=0, value=110)

    submitted_p = st.form_submit_button("新增 / 更新個人補運資料")
    if submitted_p:
      df_p = st.session_state.data_personal
      if year_p in df_p["年份"].values:
        df_p.loc[df_p["年份"] == year_p, "補運月份"] = p_fortune_month
        df_p.loc[df_p["年份"] == year_p, "補運人數"] = p_fortune_count
        df_p.loc[df_p["年份"] == year_p, "補財庫月份"] = p_wealth_month
        df_p.loc[df_p["年份"] == year_p, "補財庫人數"] = p_wealth_count
      else:
        new_row = pd.DataFrame({
            "年份": [year_p],
            "補運月份": [p_fortune_month],
            "補運人數": [p_fortune_count],
            "補財庫月份": [p_wealth_month],
            "補財庫人數": [p_wealth_count],
        })
        st.session_state.data_personal = pd.concat(
            [df_p, new_row], ignore_index=True
        )
      st.session_state.data_personal = (
          st.session_state.data_personal.sort_values("年份").reset_index(
              drop=True
          )
      )
      st.success(f"成功儲存 {year_p} 年個人補運及補財庫資料！")

  st.subheader("📊 個人補運及補財庫人數總覽表")
  st.dataframe(st.session_state.data_personal, use_container_width=True)

  df_personal = st.session_state.data_personal
  fig_personal = make_subplots(specs=[[{"secondary_y": True}]])
  personal_series = [
      (
          "補運月份", "補運人數", "六月補運人數", "purple", "solid", False,
          "六月補運",
      ),
      (
          "補運月份", "補運人數", "九月補運人數", "mediumpurple", "dash",
          False, "九月補運",
      ),
      (
          "補財庫月份", "補財庫人數", "六月補財庫人數", "teal", "solid",
          True, "六月補財庫",
      ),
      (
          "補財庫月份", "補財庫人數", "九月補財庫人數", "darkcyan", "dash",
          True, "九月補財庫",
      ),
  ]
  for (
      month_column, count_column, name, color, dash, secondary_y, month
  ) in personal_series:
      month_data = df_personal[df_personal[month_column] == month]
      fig_personal.add_trace(
          go.Scatter(
              x=month_data["年份"],
              y=month_data[count_column],
              name=name,
              mode="lines+markers",
              line=dict(color=color, width=3, dash=dash),
          ),
          secondary_y=secondary_y,
      )
  fig_personal.update_layout(
      title="個人補運及補財庫報名人數分佈圖",
      xaxis_title="年份補運",
      template="plotly_white",
  )
  fig_personal.update_yaxes(title_text="<b>補運人數</b>", secondary_y=False)
  fig_personal.update_yaxes(title_text="<b>補財庫人數</b>", secondary_y=True)
  st.plotly_chart(fig_personal, use_container_width=True)
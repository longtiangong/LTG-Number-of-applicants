import math
import os

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st


def configure_year_axis(fig, dataframe):
    years = sorted(int(year) for year in dataframe["年份"].dropna().unique())
    if not years:
        years = [2026]
    fig.update_xaxes(
        tickmode="array",
        tickvals=years,
        ticktext=[str(year) for year in years],
        range=[years[0] - 0.25, years[-1] + 0.25],
    )


def configure_y_axes(fig, chart_key, axes):
    with st.expander("調整Y軸上下限與刻度間距"):
        for axis_key, title, dataframe, columns, secondary_y in axes:
            st.markdown(f"**{title}**")
            values = dataframe[columns].max().max()
            data_max = 0 if pd.isna(values) else max(0, int(values))
            default_max = max(50, math.ceil(data_max / 50) * 50 + 50)
            default_interval = max(1, default_max // 5)

            lower_col, upper_col, interval_col = st.columns(3)
            with lower_col:
                lower = st.number_input(
                    "Y軸下限",
                    min_value=0,
                    value=0,
                    step=1,
                    key=f"{chart_key}_{axis_key}_lower",
                )
            with upper_col:
                upper = st.number_input(
                    "Y軸上限",
                    min_value=1,
                    value=default_max,
                    step=1,
                    key=f"{chart_key}_{axis_key}_upper",
                )
            with interval_col:
                interval = st.number_input(
                    "刻度間距",
                    min_value=1,
                    value=default_interval,
                    step=1,
                    key=f"{chart_key}_{axis_key}_interval",
                )

            if upper <= lower:
                st.error(f"{title}的Y軸上限必須大於下限。")
                continue
            axis_options = {
                "range": [lower, upper],
                "dtick": interval,
            }
            if secondary_y is not None:
                axis_options["secondary_y"] = secondary_y
            fig.update_yaxes(**axis_options)


def build_annual_summary(dataframes):
    summary = None
    for dataframe, count_columns in dataframes:
        yearly_counts = dataframe[["年份", *count_columns]].groupby(
            "年份", as_index=False
        )[count_columns].sum()
        summary = (
            yearly_counts
            if summary is None
            else summary.merge(yearly_counts, on="年份", how="outer")
        )

    if summary is None:
        return pd.DataFrame(columns=["年份"])
    return (
        summary.fillna(0)
        .sort_values("年份")
        .astype({"年份": int, **{column: int for column in summary.columns[1:]}})
        .reset_index(drop=True)
    )


# 設定網頁標題與寬度
st.set_page_config(
    page_title="龍天宮歷年活動報名人數系統", page_icon="🏮", layout="wide"
)

app_version = os.getenv("APP_VERSION", "").strip()
st.title(f"🏮 龍天宮歷年活動報名人數統計與分佈系統（{app_version}")

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

personal_count_columns = [
    "六月補運人數",
    "九月補運人數",
    "六月補財庫人數",
    "九月補財庫人數",
]

if "data_personal" not in st.session_state:
    st.session_state.data_personal = pd.DataFrame(
        {
            "年份": [2024, 2025, 2026],
            "六月補運人數": [120, 0, 150],
            "九月補運人數": [0, 135, 0],
            "六月補財庫人數": [85, 0, 100],
            "九月補財庫人數": [0, 95, 0],
        }
    )
elif not set(personal_count_columns).issubset(
    st.session_state.data_personal.columns
):
    legacy_columns = {
        "年份",
        "補運月份",
        "補運人數",
        "補財庫月份",
        "補財庫人數",
    }
    if not legacy_columns.issubset(st.session_state.data_personal.columns):
        raise ValueError("個人補運資料欄位不完整，無法轉換舊資料。")

    legacy_personal = st.session_state.data_personal
    migrated_personal = pd.DataFrame(
        {
            "年份": legacy_personal["年份"],
            "六月補運人數": 0,
            "九月補運人數": 0,
            "六月補財庫人數": 0,
            "九月補財庫人數": 0,
        }
    )
    for month, count_column in (
        ("六月補運", "六月補運人數"),
        ("九月補運", "九月補運人數"),
    ):
        matching_years = legacy_personal["補運月份"] == month
        migrated_personal.loc[matching_years, count_column] = (
            legacy_personal.loc[matching_years, "補運人數"]
        )
    for months, count_column in (
        (("六月補運", "六月補財庫"), "六月補財庫人數"),
        (("九月補運", "九月補財庫"), "九月補財庫人數"),
    ):
        matching_years = legacy_personal["補財庫月份"].isin(months)
        migrated_personal.loc[matching_years, count_column] = (
            legacy_personal.loc[matching_years, "補財庫人數"]
        )
    st.session_state.data_personal = migrated_personal

if "data_pudu" not in st.session_state:
        st.session_state.data_pudu = pd.DataFrame(columns=["年份", "普度人數"])

# 建立活動管理及年度看板分頁
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
        [
            "1. 正月祭改",
            "2. 正月光明燈及太歲",
            "3. 正月年斗",
            "4. 三月全家補運及補財庫",
            "5. 個人補運及補財庫",
            "6. 普度",
            "7. 年度看板",
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
  configure_year_axis(fig_jg, df_jg)
  configure_y_axes(
      fig_jg,
      "jg",
      [("count", "祭改人數", df_jg, ["祭改人數"], None)],
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
          customdata=df_light["年份"],
          name="300元光明燈人數",
          hovertemplate=(
              "年份: %{customdata}<br>300元光明燈人數: %{y}<extra></extra>"
          ),
          line=dict(color="orange", width=3),
          mode="lines+markers",
      ),
      secondary_y=False,
  )
  fig_light.add_trace(
      go.Scatter(
          x=df_light["年份"],
          y=df_light["500元光明燈"],
          customdata=df_light["年份"],
          name="500元光明燈人數",
          hovertemplate=(
              "年份: %{customdata}<br>500元光明燈人數: %{y}<extra></extra>"
          ),
          line=dict(color="orangered", width=3, dash="dash"),
          mode="lines+markers",
      ),
      secondary_y=True,
  )
  fig_light.update_layout(
      title="正月光明燈報名人數分佈圖", xaxis_title="年份光明燈", template="plotly_white"
  )
  fig_light.update_yaxes(title_text="<b>300元光明燈人數</b>", secondary_y=False)
  fig_light.update_yaxes(title_text="<b>500元光明燈人數</b>", secondary_y=True)
  configure_year_axis(fig_light, df_light)
  configure_y_axes(
      fig_light,
      "light",
      [
          ("300", "300元光明燈人數", df_light, ["300元光明燈"], False),
          ("500", "500元光明燈人數", df_light, ["500元光明燈"], True),
      ],
  )
  st.plotly_chart(fig_light, use_container_width=True)

  # 圖表 2：太歲雙Y軸曲線圖
  fig_taisu = make_subplots(specs=[[{"secondary_y": True}]])
  fig_taisu.add_trace(
      go.Scatter(
          x=df_light["年份"],
          y=df_light["300元太歲"],
          customdata=df_light["年份"],
          name="300元太歲人數",
          hovertemplate=(
              "年份: %{customdata}<br>300元太歲人數: %{y}<extra></extra>"
          ),
          line=dict(color="dodgerblue", width=3),
          mode="lines+markers",
      ),
      secondary_y=False,
  )
  fig_taisu.add_trace(
      go.Scatter(
          x=df_light["年份"],
          y=df_light["500元太歲"],
          customdata=df_light["年份"],
          name="500元太歲人數",
          hovertemplate=(
              "年份: %{customdata}<br>500元太歲人數: %{y}<extra></extra>"
          ),
          line=dict(color="darkblue", width=3, dash="dash"),
          mode="lines+markers",
      ),
      secondary_y=True,
  )
  fig_taisu.update_layout(
      title="正月太歲報名人數分佈圖", xaxis_title="年份太歲", template="plotly_white"
  )
  fig_taisu.update_yaxes(title_text="<b>300元太歲人數</b>", secondary_y=False)
  fig_taisu.update_yaxes(title_text="<b>500元太歲人數</b>", secondary_y=True)
  configure_year_axis(fig_taisu, df_light)
  configure_y_axes(
      fig_taisu,
      "taisu",
      [
          ("300", "300元太歲人數", df_light, ["300元太歲"], False),
          ("500", "500元太歲人數", df_light, ["500元太歲"], True),
      ],
  )
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
  configure_year_axis(fig_dou, df_dou)
  configure_y_axes(
      fig_dou,
      "dou",
      [(
          "count",
          "年斗人數",
          df_dou,
          ["1000元年斗", "3000元年斗", "5000元年斗", "6000元年斗"],
          None,
      )],
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
          customdata=df_march["年份"],
          name="全家補運人數",
          hovertemplate=(
              "年份: %{customdata}<br>全家補運人數: %{y}<extra></extra>"
          ),
          line=dict(color="green", width=3),
          mode="lines+markers",
      ),
      secondary_y=False,
  )
  fig_march.add_trace(
      go.Scatter(
          x=df_march["年份"],
          y=df_march["補財庫人數"],
          customdata=df_march["年份"],
          name="補財庫人數",
          hovertemplate=(
              "年份: %{customdata}<br>補財庫人數: %{y}<extra></extra>"
          ),
          line=dict(color="goldenrod", width=3, dash="dash"),
          mode="lines+markers",
          marker=dict(symbol="diamond"),
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
  configure_year_axis(fig_march, df_march)
  configure_y_axes(
      fig_march,
      "march",
      [
          ("fortune", "全家補運人數", df_march, ["全家補運人數"], False),
          ("wealth", "補財庫人數", df_march, ["補財庫人數"], True),
      ],
  )
  st.plotly_chart(fig_march, use_container_width=True)

# ==================== 5. 個人補運及補財庫 ====================
with tab5:
  st.header("🧧 個人補運及補財庫報名管理")

  year_p = st.number_input(
      "年份", min_value=2000, max_value=2100, value=2027, step=1, key="y_pe"
  )
  df_p = st.session_state.data_personal
  existing_personal = df_p.loc[df_p["年份"] == year_p]
  current_personal = (
      existing_personal.iloc[0]
      if not existing_personal.empty
      else pd.Series({column: 0 for column in personal_count_columns})
  )

  with st.form("form_personal"):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
      p_june_fortune = st.number_input(
          "六月補運人數",
          min_value=0,
          value=int(current_personal["六月補運人數"]),
          key=f"p_june_fortune_{year_p}",
      )
    with col2:
      p_september_fortune = st.number_input(
          "九月補運人數",
          min_value=0,
          value=int(current_personal["九月補運人數"]),
          key=f"p_september_fortune_{year_p}",
      )
    with col3:
      p_june_wealth = st.number_input(
          "六月補財庫人數",
          min_value=0,
          value=int(current_personal["六月補財庫人數"]),
          key=f"p_june_wealth_{year_p}",
      )
    with col4:
      p_september_wealth = st.number_input(
          "九月補財庫人數",
          min_value=0,
          value=int(current_personal["九月補財庫人數"]),
          key=f"p_september_wealth_{year_p}",
      )

    submitted_p = st.form_submit_button("新增 / 更新個人補運資料")
    if submitted_p:
      if year_p in df_p["年份"].values:
        df_p.loc[df_p["年份"] == year_p, personal_count_columns] = [
            p_june_fortune,
            p_september_fortune,
            p_june_wealth,
            p_september_wealth,
        ]
      else:
        new_row = pd.DataFrame({
            "年份": [year_p],
            "六月補運人數": [p_june_fortune],
            "九月補運人數": [p_september_fortune],
            "六月補財庫人數": [p_june_wealth],
            "九月補財庫人數": [p_september_wealth],
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
      ("六月補運人數", "六月補運人數", "purple", "solid", False),
      ("九月補運人數", "九月補運人數", "mediumpurple", "dash", False),
      ("六月補財庫人數", "六月補財庫人數", "teal", "solid", True),
      ("九月補財庫人數", "九月補財庫人數", "darkcyan", "dash", True),
  ]
  for (
      count_column, name, color, dash, secondary_y
  ) in personal_series:
      fig_personal.add_trace(
          go.Scatter(
              x=df_personal["年份"],
              y=df_personal[count_column],
              customdata=df_personal["年份"],
              name=name,
              mode="lines+markers",
              hovertemplate=(
                  f"年份: %{{customdata}}<br>{name}: %{{y}}<extra></extra>"
              ),
              line=dict(color=color, width=3, dash=dash),
              marker=dict(symbol="diamond" if secondary_y else "circle"),
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
  configure_year_axis(fig_personal, df_personal)
  configure_y_axes(
      fig_personal,
      "personal",
      [
          (
              "fortune",
              "補運人數",
              df_personal,
              ["六月補運人數", "九月補運人數"],
              False,
          ),
          (
              "wealth",
              "補財庫人數",
              df_personal,
              ["六月補財庫人數", "九月補財庫人數"],
              True,
          ),
      ],
  )
  st.plotly_chart(fig_personal, use_container_width=True)

# ==================== 6. 普度 ====================
with tab6:
  st.header("🙏 普度報名管理")

  with st.form("form_pudu"):
    col1, col2 = st.columns(2)
    with col1:
      year_pudu = st.number_input(
          "年份", min_value=2000, max_value=2100, value=2026, step=1, key="y_pudu"
      )
    with col2:
      count_pudu = st.number_input(
          "普度人數", min_value=0, value=150, step=1, key="c_pudu"
      )

    submitted_pudu = st.form_submit_button("新增 / 更新普度資料")
    if submitted_pudu:
      df_pudu = st.session_state.data_pudu
      if year_pudu in df_pudu["年份"].values:
        df_pudu.loc[df_pudu["年份"] == year_pudu, "普度人數"] = count_pudu
      else:
        new_row = pd.DataFrame({"年份": [year_pudu], "普度人數": [count_pudu]})
        st.session_state.data_pudu = pd.concat(
            [df_pudu, new_row], ignore_index=True
        )
      st.session_state.data_pudu = st.session_state.data_pudu.sort_values(
          "年份"
      ).reset_index(drop=True)
      st.success(f"成功儲存 {year_pudu} 年普度資料！")

  st.subheader("📊 普度人數總覽表")
  st.dataframe(st.session_state.data_pudu, use_container_width=True)

  df_pudu = st.session_state.data_pudu
  fig_pudu = go.Figure()
  fig_pudu.add_trace(
      go.Scatter(
          x=df_pudu["年份"],
          y=df_pudu["普度人數"],
          mode="lines+markers",
          name="普度人數",
          line=dict(color="darkorange", width=3),
      )
  )
  fig_pudu.update_layout(
      title="普度人數分佈圖",
      xaxis_title="年份普度",
      yaxis_title="普度人數",
      template="plotly_white",
  )
  configure_year_axis(fig_pudu, df_pudu)
  configure_y_axes(
      fig_pudu,
      "pudu",
      [("count", "普度人數", df_pudu, ["普度人數"], None)],
  )
  st.plotly_chart(fig_pudu, use_container_width=True)

# ==================== 7. 年度看板 ====================
with tab7:
  st.header("📈 歷年活動報名人數看板")

  annual_summary = build_annual_summary(
      [
          (st.session_state.data_jg, ["祭改人數"]),
          (
              st.session_state.data_light,
              ["300元光明燈", "500元光明燈"],
          ),
          (
              st.session_state.data_light,
              ["300元太歲", "500元太歲"],
          ),
          (
              st.session_state.data_dou,
              [
                  "1000元年斗",
                  "3000元年斗",
                  "5000元年斗",
                  "6000元年斗",
              ],
          ),
          (
              st.session_state.data_march,
              ["全家補運人數", "補財庫人數"],
          ),
          (
              st.session_state.data_personal,
              personal_count_columns,
          ),
          (st.session_state.data_pudu, ["普度人數"]),
      ]
  )
  activity_columns = {
      "祭改": ["祭改人數"],
      "光明燈": ["300元光明燈", "500元光明燈"],
      "太歲": ["300元太歲", "500元太歲"],
      "正月年斗": [
          "1000元年斗",
          "3000元年斗",
          "5000元年斗",
          "6000元年斗",
      ],
      "三月全家補運及補財庫": ["全家補運人數", "補財庫人數"],
      "個人補運及補財庫": personal_count_columns,
      "普度": ["普度人數"],
  }
  annual_category_totals = annual_summary[["年份"]].copy()
  for activity, columns in activity_columns.items():
      total_column = f"{activity}總計"
      annual_category_totals[total_column] = annual_summary[columns].sum(axis=1)

  st.subheader("📋 各年度活動報名人數總表")
  st.dataframe(annual_summary, use_container_width=True, hide_index=True)
  st.subheader("📊 各類活動報名人數總計表")
  st.dataframe(annual_category_totals, use_container_width=True, hide_index=True)

  years = annual_summary["年份"].tolist()
  if not years:
      st.info("目前沒有可供比較的年度資料。")
  else:
      selected_activity = st.selectbox(
          "選擇比較活動",
          list(activity_columns),
          key="dashboard_activity",
      )
      left_year, right_year = st.columns(2)
      with left_year:
          selected_left_year = st.selectbox(
              "左側圖表年份",
              years,
              index=max(0, len(years) - 2),
              key="dashboard_left_year",
          )
      with right_year:
          selected_right_year = st.selectbox(
              "右側圖表年份",
              years,
              index=len(years) - 1,
              key="dashboard_right_year",
          )

      chart_columns = st.columns(2)
      for chart_column, selected_year, side in (
          (chart_columns[0], selected_left_year, "left"),
          (chart_columns[1], selected_right_year, "right"),
      ):
          with chart_column:
              activity_count_columns = activity_columns[selected_activity]
              year_data = annual_summary.loc[
                  annual_summary["年份"] == selected_year
              ].iloc[0]
              bar_labels = [
                  column.removesuffix("人數")
                  for column in activity_count_columns
              ]
              bar_values = [
                  int(year_data[column]) for column in activity_count_columns
              ]
              bar_labels.append("總計")
              bar_values.append(sum(bar_values))

              fig_breakdown = go.Figure(
                  go.Bar(
                      x=bar_labels,
                      y=bar_values,
                      text=bar_values,
                      textposition="outside",
                      marker_color=[
                          "steelblue"
                          if label != "總計"
                          else "darkorange"
                          for label in bar_labels
                      ],
                      hovertemplate=(
                          "%{x}: %{y}人<extra></extra>"
                      ),
                  )
              )
              fig_breakdown.update_layout(
                  title=f"{selected_year}年{selected_activity}報名人數",
                  xaxis_title="方案／項目",
                  yaxis_title="報名人數",
                  template="plotly_white",
                  showlegend=False,
              )
              fig_breakdown.update_yaxes(rangemode="tozero")
              st.plotly_chart(
                  fig_breakdown,
                  use_container_width=True,
                  key=f"dashboard_{side}_breakdown",
              )

import streamlit as st
import json
from pathlib import Path
from pprint import pprint


def load_json(file):
    try:
        contents = file.gevalue().decode("utf-8")
        return jsong.load(contents)
    except:
        st.errror(f"error loading json file: {str(e)}")
        return None


def load_local_json(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading JSON file: {str(e)}")
        return None


def get_cur_conf():
    output_settings = {"contents": []}
    for item in config["contents"]:
        key = f"input_{item['name']}"
        if key in st.session_state:
            output_settings["contents"].append(
                {
                    "name": item["name"],
                    "unit": item["unit"],
                    "value": st.session_state[key],
                    "upper": item["upper"],
                    "lower": item["lower"],
                    "help": item["help"],
                }
            )

    pprint(output_settings)


# 페이지 설정
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# CSS로 사이드바를 오른쪽으로 이동
st.markdown(
    """
    <style>
        [data-testid="stSidebar"][aria-expanded="true"]{
            margin-left: 0;
            margin-right: 0;
            left: unset;
            right: 0;
        }
        [data-testid="stSidebar"][aria-expanded="false"]{
            margin-left: 0;
            margin-right: 0;
            left: unset;
            right: -100%;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


st.title("Config Viewer")

# config_file = st.file_uploader("Upload JSON file", type=["json"])
# if config_file is not None:
#     config = load_json(config_file)
# else:
#     st.info("Please upload a JSON file")
#     st.stop()

config = load_local_json("config.json")

if config:
    with st.sidebar:
        st.header("Parameter Settings")

        # 검색 필터
        search_term = st.text_input("Search parameters", "")

        # 카테고리 필터 (Temperature, Pressure 등)
        categories = sorted(list(set([item["name"] for item in config["contents"]])))
        selected_category = st.selectbox("Filter by category", ["All"] + categories)

        # 필터링된 항목 표시
        filtered_items = config["contents"]
        if search_term:
            filtered_items = [
                item
                for item in filtered_items
                if search_term.lower() in item["name"].lower()
            ]
        if selected_category != "All":
            filtered_items = [
                item
                for item in filtered_items
                if item["name"].startswith(selected_category)
            ]

        # 파라미터 표시
        st.subheader("Parameters")
        for item in filtered_items:
            with st.expander(f"{item['name']} ({item['unit']})"):
                value = st.number_input(
                    "Value",
                    min_value=float(item["lower"]),
                    max_value=float(item["upper"]),
                    value=float(item["lower"]),
                    key=f"input_{item['name']}",
                )
                st.info(item["help"])
                st.text(f"Range: {item['lower']} to {item['upper']} {item['unit']}")

    #################################
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Current Settings")
        current_settings = {
            name: st.session_state[f"input_{name}"]
            for item in config["contents"]
            if f"input_{item['name']}" in st.session_state and (name := item["name"])
        }
        st.json(current_settings)

    with col2:
        st.subheader("Selected Category Info")
        if selected_category != "All":
            category_items = [
                item
                for item in config["contents"]
                if item["name"].startswith(selected_category)
            ]
            st.write(f"Total items in {selected_category}: {len(category_items)}")

            # 카테고리 통계
            if category_items:
                avg_upper = sum(item["upper"] for item in category_items) / len(
                    category_items
                )
                avg_lower = sum(item["lower"] for item in category_items) / len(
                    category_items
                )
                st.write(f"Average range: {avg_lower:.2f} to {avg_upper:.2f}")
    ############################
    if st.sidebar.button("Save Settings", type="primary"):
        get_cur_conf()
        # try:
        #     # 현재 모든 설정값 수집
        #     output_settings = {"contents": []}
        #     for item in config["contents"]:
        #         key = f"input_{item['name']}"
        #         if key in st.session_state:
        #             output_settings["contents"].append(
        #                 {
        #                     "name": item["name"],
        #                     "unit": item["unit"],
        #                     "value": st.session_state[key],
        #                     "upper": item["upper"],
        #                     "lower": item["lower"],
        #                     "help": item["help"],
        #                 }
        #             )

        #     # JSON 파일로 저장
        #     output_file = "saved_config.json"
        #     with open(output_file, "w", encoding="utf-8") as f:
        #         json.dump(output_settings, f, indent=2)

        #     # 다운로드 버튼 생성
        #     with open(output_file, "r", encoding="utf-8") as f:
        #         st.sidebar.download_button(
        #             label="Download Config",
        #             data=f.read(),
        #             file_name="saved_config.json",
        #             mime="application/json",
        #         )

        #     st.sidebar.success("Settings saved successfully!")

        # except Exception as e:
        #     st.sidebar.error(f"Error saving settings: {str(e)}")

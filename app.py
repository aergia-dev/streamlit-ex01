import streamlit as st
import json
import os


def load_json_config(file_path):
    """JSON 설정 파일을 로드하는 함수"""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        st.error(f"설정 파일을 찾을 수 없습니다: {file_path}")
        return None
    except json.JSONDecodeError:
        st.error(f"잘못된 JSON 형식입니다: {file_path}")
        return None


def get_filtered_items(data, search_term):
    """검색어에 맞는 아이템들을 찾는 함수"""
    filtered_items = []
    for main_category, categories in data.items():
        for category, items in categories.items():
            for item_name, item_data in items.items():
                if search_term.lower() in item_name.lower():
                    filtered_items.append(
                        {
                            "main_category": main_category,
                            "category": category,
                            "item_name": item_name,
                            "item_data": item_data,
                        }
                    )
    return filtered_items


def get_item_value(item_name):
    """아이템의 현재 값을 가져오는 함수"""
    return st.session_state.get(f"value_{item_name}", 0.0)


def update_value(item_name, value):
    """아이템의 값을 업데이트하는 함수"""
    st.session_state[f"value_{item_name}"] = value


def get_all_changed_values():
    """변경된 모든 값을 가져오는 함수"""
    changed_values = {}
    for key in st.session_state:
        if key.startswith("value_"):
            item_name = key.replace("value_", "")
            changed_values[item_name] = st.session_state[key]
    return changed_values


def render_item_row(name, data, key_prefix):
    """아이템 한 줄을 렌더링하는 함수"""
    cols = st.columns([1, 1])
    with cols[0]:
        st.markdown(f"**{name}**")
    with cols[1]:
        value = st.number_input(
            "",
            min_value=float(data["lower"]),
            max_value=float(data["upper"]),
            value=float(data["value"]),
            step=float(data["unit"]),
            key=f"{key_prefix}_{name}",
        )
        update_value(name, value)


def main():
    st.title("Configuration Interface")

    # 메인 화면에 변경된 값 표시
    changed_values = get_all_changed_values()
    if changed_values:
        st.markdown("### Changed Values")
        for item_name, value in changed_values.items():
            st.write(f"**{item_name}**: {value}")

    # 사이드바 구성
    with st.sidebar:
        # 파일 업로더
        uploaded_file = st.file_uploader("Upload JSON Config", type=["json"])

        # 데이터 로드
        if uploaded_file is not None:
            try:
                data = json.load(uploaded_file)
            except Exception as e:
                st.error(f"JSON 파일 로드 중 오류 발생: {str(e)}")
                return
        else:
            default_config_path = "config.json"
            if os.path.exists(default_config_path):
                data = load_json_config(default_config_path)
            else:
                st.error("설정 파일을 업로드하거나 기본 설정 파일을 제공해주세요.")
                return

        if data is None:
            return

        # 검색 기능
        search_term = st.text_input("Search items:", "")

        if search_term:
            # 검색어가 있는 경우 검색 결과 표시
            filtered_items = get_filtered_items(data, search_term)
            if filtered_items:
                st.write(f"Found {len(filtered_items)} items:")
                # 검색 결과를 리스트로 표시
                for item in filtered_items:
                    st.markdown(f"**{item['item_name']}**")
                    st.markdown(f"Category: {item['category']}")
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        value = st.number_input(
                            "Value",
                            min_value=item["item_data"]["lower"],
                            max_value=item["item_data"]["upper"],
                            value=0,
                            step=item["item_data"]["unit"],
                            help=item["item_data"]["help"],
                            key=f"search_{item['item_name']}",
                        )
                    with col2:
                        st.text(f"Unit: {item['item_data']['unit']}")
                    st.markdown("---")
            else:
                st.write("No items found.")
        else:
            # 메인 카테고리 선택 콤보박스

            selected_main = st.radio("Select Main Category:", options=list(data.keys()))

            # 선택된 메인 카테고리의 내용 표시
            if selected_main:
                selected_data = data[selected_main]

                for category, items in selected_data.items():
                    with st.expander(f"{category}", True):
                        # 아이템 표시
                        for item_name, item_data in items.items():
                            render_item_row(item_name, item_data, category)

        # 설정 다운로드 버튼
        if st.button("Download Current Config"):
            json_str = json.dumps(data, indent=4)
            st.download_button(
                label="Download JSON",
                file_name="config.json",
                mime="application/json",
                data=json_str,
            )


if __name__ == "__main__":
    main()

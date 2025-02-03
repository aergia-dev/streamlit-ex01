import streamlit as st
import json
import os
import re
from copy import deepcopy
import numexpr as ne


## use singletone to save data
class Config:
    _instance = None
    _data = None

    @classmethod
    def get_instance(cls, initial_data=None):
        if cls._instance is None:
            cls._instance = cls()
            cls._data = deepcopy(initial_data) if initial_data else None
        return cls._instance

    @classmethod
    def get_expr_value(cls, expr):
        # todo: hardcoding
        print(f"expppr {expr}")
        parts = re.split("([\(\)+\-*/%,])", expr)
        print(f"parts {parts}")
        result = []
        for part in parts:
            part = part.strip()
            if "##" in part:
                print(f"part {part}")
                main_cat, sub_cat, item = part.split("##")

                try:
                    if "value" in cls._data[main_cat][sub_cat][item]:
                        value = cls._data[main_cat][sub_cat][item]["value"]
                    else:
                        print(f"not value  {cls._data[main_cat][sub_cat][item]["expr"]}")
                        value = cls.get_expr_value(cls._data[main_cat][sub_cat][item]["expr"])
                    result.append(str(value))
                except:
                    result.append(part)
            else:
                result.append(part)
        
        # print(f"result {result}")
        return " ".join(result)

    @classmethod
    def update_value(cls, key_prefix, new_val):
        print("update_value")
        main_cat, sub_cat, item = re.split("##", key_prefix)
        cls._data[main_cat][sub_cat][item]['value'] = new_val
        print(f"key_prefix {key_prefix}, new val: {new_val}")
        print(f"data[{main_cat}][{sub_cat}][{item}]")

def load_json_config(file_path):
    """JSON 설정 파일을 로드하는 함수"""
    try:
        with open(file_path, "r", encoding="utf_8") as file:
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

def input_on_change(key_prefix, new_val):
    print(f"category {key_prefix}")
    print(f"new val {new_val}")
    Config.update_value(key_prefix, new_val)


def render_item_row(name, data, category):
    category.append(name)
    key_prefix = "##".join(category)
    category.pop()

    cols = st.columns([1, 1])
    with cols[0]:
        st.markdown(f"**{name}**")
    with cols[1]:
        if "value" in data:
            value = st.number_input(
                "",
                min_value=float(data["lower"]),
                max_value=float(data["upper"]),
                value=float(data["value"]),
                step=float(data["unit"]),
                key=key_prefix,
                on_change=lambda: input_on_change(key_prefix, st.session_state[key_prefix])
            )
        else:
            item_value = Config.get_expr_value(data['expr']).replace(" ", "")
            print(f"item_value {item_value}")
            # ne.evalute: max(4,4*2/4) is not working
            # item_value = ne.evaluate(item_value)
            # eval: not prepared for securty
            item_value = eval(item_value)
            value = st.number_input(
                "",
                # min_value=float(data["lower"]),
                # max_value=float(data["upper"]),
                value=float(item_value),
                disabled=True,
                key=key_prefix,
                on_change=lambda: input_on_change(key_prefix, st.session_state[key_prefix])
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
        else:
            # init data
            Config.get_instance(data)

        category = []
        main_cat = st.radio("Select Main Category:", options=list(data.keys()))
        category.append(main_cat)

        # 선택된 메인 카테고리의 내용 표시
        if main_cat:
            selected_data = data[main_cat]

            for sub_cat, items in selected_data.items():
                category.append(sub_cat)
                with st.expander(f"{sub_cat}", True):
                    # 아이템 표시
                    for item_name, item_data in items.items():
                        render_item_row(item_name, item_data, category)
                category.pop()

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

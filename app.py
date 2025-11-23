import streamlit as st
import duckdb
import pandas as pd
import time

# ---------------------------------------------
# 1) DuckDB 연결 (GitHub에 업로드된 DB 파일명 그대로!)
# ---------------------------------------------
conn = duckdb.connect("마당 (4).db")

# 쿼리 실행 함수
def query(sql, fetch_type="df"):
    try:
        if sql.strip().upper().startswith("SELECT"):
            if fetch_type == "df":
                return conn.execute(sql).fetchdf()
            else:
                return conn.execute(sql).fetchall()
        else:
            conn.execute(sql)
            conn.commit()
            return None
    except Exception as e:
        st.error(f"쿼리 실행 오류 발생: {e}")
        return None


# ---------------------------------------------
# 2) 초기 데이터 (Book 테이블에서 책 목록 로드)
# ---------------------------------------------
books = [None]

result_df = query("SELECT bookid, bookname FROM Book")

if result_df is not None and not result_df.empty:
    for _, row in result_df.iterrows():
        books.append(f"{row['bookid']},{row['bookname']}")
else:
    st.error("Book 테이블 로딩 실패. DB 파일 확인 필요.")


# ---------------------------------------------
# 3) Streamlit UI 시작
# ---------------------------------------------
st.title("📚 마당 도서 관리 시스템 (DuckDB)")

tab1, tab2 = st.tabs(["고객조회", "거래 입력 및 고객 등록"])


# ---------------------------------------------
# 📌 탭 1: 고객 조회
# ---------------------------------------------
with tab1:
    st.header("고객 조회")

    name = st.text_input("조회할 고객명")

    if len(name) > 0:
        sql_select = f"""
        SELECT c.custid, c.name, b.bookname, o.orderdate, o.saleprice 
        FROM Customer c 
        LEFT JOIN Orders o ON c.custid = o.custid 
        LEFT JOIN Book b ON o.bookid = b.bookid
        WHERE c.name = '{name}'
        ORDER BY o.orderdate DESC NULLS LAST
        """

        result_df = query(sql_select, "df")

        if result_df is not None and not result_df.empty:

            order_history = result_df[result_df["bookname"].notna()]

            st.subheader(f"'{name}' 님의 주문 내역")

            if not order_history.empty:
                st.dataframe(order_history[["bookname", "orderdate", "saleprice"]],
                             use_container_width=True)
            else:
                st.info(f"'{name}' 님의 주문 내역이 없습니다.")

            custid = result_df["custid"].iloc[0]
            st.session_state["current_custid"] = custid
            st.session_state["current_name"] = name

            st.caption(f"현재 고객 번호: {custid}")

        else:
            st.warning(f"고객 '{name}'이(가) 없습니다. 신규 등록 가능.")
            st.session_state["current_custid"] = None
            st.session_state["current_name"] = name


# ---------------------------------------------
# 📌 탭 2: 고객 등록 & 거래 입력
# ---------------------------------------------
with tab2:
    st.header("거래 입력 및 고객 등록")

    current_custid = st.session_state.get("current_custid")
    current_name = st.session_state.get("current_name", "")

    # ----- 고객 등록 -----
    st.subheader("신규 고객 등록 (과제)")

    new_name = st.text_input("등록할 이름 (필수)")
    new_address = st.text_input("주소")
    new_phone = st.text_input("전화번호 (예: 010-1234-5678)")

    if st.button("고객 등록"):
        if new_name:
            max_id_df = query("SELECT MAX(custid) AS max_id FROM Customer", "df")
            if max_id_df is not None and not max_id_df.empty:
                max_id = max_id_df["max_id"].iloc[0]
            else:
                max_id = 0

            new_custid = (max_id + 1) if max_id is not None else 1

            sql_insert_cust = f"""
            INSERT INTO Customer (custid, name, address, phone)
            VALUES ({new_custid}, '{new_name}', '{new_address}', '{new_phone}')
            """
            query(sql_insert_cust, "none")

            st.success(f"신규 고객 '{new_name}' (ID: {new_custid}) 등록 완료!")
            st.session_state["current_custid"] = new_custid
            st.session_state["current_name"] = new_name

            st.rerun()

        else:
            st.warning("이름은 필수 입력입니다.")

    st.markdown("---")

    # ----- 거래 입력 -----
    st.subheader("도서 거래 입력")

    if current_custid:
        st.info(f"현재 고객: {current_name} (ID: {current_custid})")

        select_book = st.selectbox("구매 서적:", books)

        if select_book and select_book != "None":
            bookid_str, bookname = select_book.split(",", 1)
            bookid = int(bookid_str)

            price = st.number_input("구매 금액", min_value=1, step=1000)

            dt = time.strftime("%Y-%m-%d", time.localtime())

            if st.button("거래 입력 (과제)"):
                max_order_df = query("SELECT MAX(orderid) AS max_id FROM Orders", "df")
                max_order_id = max_order_df["max_id"].iloc[0] if max_order_df is not None else 0

                new_orderid = (max_order_id + 1) if max_order_id is not None else 1

                sql_insert_order = f"""
                INSERT INTO Orders (orderid, custid, bookid, saleprice, orderdate)
                VALUES ({new_orderid}, {current_custid}, {bookid}, {price}, '{dt}')
                """

                query(sql_insert_order, "none")
                st.success("거래 입력 성공!")

        else:
            st.warning("구매할 책을 선택해 주세요.")
    else:
        st.warning("고객을 먼저 조회하거나 신규 고객을 등록하세요.")

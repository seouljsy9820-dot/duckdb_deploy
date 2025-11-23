import streamlit as st
import duckdb
import pandas as pd
import time

# --- 1) DB 연결 ---
DB_FILE = 'madang.db'
conn = duckdb.connect(DB_FILE)

# --- 2) SQL 실행 함수 ---
def query(sql, fetch="df"):
    try:
        if sql.strip().upper().startswith("SELECT"):
            return conn.execute(sql).fetchdf() if fetch == "df" else conn.execute(sql).fetchall()
        else:
            conn.execute(sql)
            conn.commit()
    except Exception as e:
        st.error(f"SQL 실행 오류: {e}")
        return None

# --- 3) 책 목록 불러오기 ---
books = [None]
book_df = query("SELECT bookid, bookname FROM Book")

if book_df is not None:
    for _, row in book_df.iterrows():
        books.append(f"{row['bookid']},{row['bookname']}")

# --- UI 시작 ---
st.title("📚 마당 도서 관리 시스템 (DuckDB)")

tab1, tab2 = st.tabs(["고객 조회", "거래 입력 및 고객 등록"])

# -----------------------------
# 탭 1: 고객 조회
# -----------------------------
with tab1:
    st.header("고객 조회")

    name = st.text_input("조회할 고객명")

    if name:
        sql = f"""
        SELECT c.custid, c.name, b.bookname, o.orderdate, o.saleprice 
        FROM Customer c
        LEFT JOIN Orders o ON c.custid = o.custid
        LEFT JOIN Book b ON o.bookid = b.bookid
        WHERE c.name = '{name}'
        ORDER BY o.orderdate DESC NULLS LAST
        """
        df = query(sql)

        if df is not None and not df.empty:
            st.subheader(f"'{name}' 님의 주문 내역")

            order_df = df[df["bookname"].notna()]
            st.dataframe(order_df[["bookname", "orderdate", "saleprice"]], use_container_width=True)

            custid = df["custid"].iloc[0]
            st.session_state["custid"] = custid
            st.session_state["name"] = name

            st.caption(f"현재 고객 번호: {custid}")

        else:
            st.warning("등록된 고객이 없습니다. 오른쪽 탭에서 신규 고객 등록 가능.")

# -----------------------------
# 탭 2: 고객 등록 + 주문 입력
# -----------------------------
with tab2:
    st.header("거래 입력 및 고객 등록")

    current_id = st.session_state.get("custid", None)
    current_name = st.session_state.get("name", "")

    # 신규 고객 등록
    st.subheader("신규 고객 등록")
    new_name = st.text_input("이름 입력 (필수)")
    new_addr = st.text_input("주소 입력")
    new_phone = st.text_input("전화번호 입력")

    if st.button("고객 등록"):
        if new_name:
            df_max = query("SELECT MAX(custid) AS maxid FROM Customer")
            new_id = int(df_max['maxid'][0]) + 1 if df_max['maxid'][0] else 1

            sql = f"""
            INSERT INTO Customer(custid, name, address, phone)
            VALUES ({new_id}, '{new_name}', '{new_addr}', '{new_phone}')
            """
            query(sql, fetch="none")

            st.success(f"신규 고객 '{new_name}' 등록 성공!")
            st.session_state["custid"] = new_id
            st.session_state["name"] = new_name
            st.rerun()
        else:
            st.warning("이름은 반드시 입력해야 합니다.")

    st.markdown("---")

    # 주문 입력
    st.subheader("도서 주문 입력")

    if current_id:
        st.info(f"현재 고객: {current_name} (ID: {current_id})")

        selected = st.selectbox("구매할 도서 선택", books)

        if selected and selected != "None":
            bookid, bookname = selected.split(",", 1)
            bookid = int(bookid)

            price = st.number_input("판매 금액 입력", min_value=1, step=500)

            order_date = time.strftime("%Y-%m-%d")

            if st.button("주문 입력"):
                df_order = query("SELECT MAX(orderid) AS maxid FROM Orders")
                oid = int(df_order['maxid'][0]) + 1 if df_order['maxid'][0] else 1

                sql = f"""
                INSERT INTO Orders(orderid, custid, bookid, saleprice, orderdate)
                VALUES ({oid}, {current_id}, {bookid}, {price}, '{order_date}')
                """
                query(sql, fetch="none")

                st.success("주문이 성공적으로 입력되었습니다!")
    else:
        st.warning("고객 조회 탭에서 고객을 먼저 선택하거나 신규 등록하세요.")


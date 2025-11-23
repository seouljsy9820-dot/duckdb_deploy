import streamlit as st
import duckdb
import pandas as pd
import time

# DB 연결
con = duckdb.connect("madang.db")

# 조회 함수
def query(sql, fetch='df'):
    if fetch == 'df':
        return con.execute(sql).fetchdf()
    return con.execute(sql).fetchall()

# 도서 목록 불러오기
books_df = query("SELECT bookid, bookname FROM Book")
books = ["None"] + [f"{r['bookid']},{r['bookname']}" for _, r in books_df.iterrows()]

# UI
st.title("📚 마당 도서 관리 시스템 (DuckDB)")

tab1, tab2 = st.tabs(["고객 조회", "거래 입력 및 고객 등록"])

# ========== 탭 1 - 고객 조회 ==========
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

        if not df.empty:
            st.subheader(f"'{name}' 님의 주문 내역")
            st.dataframe(df[['bookname', 'orderdate', 'saleprice']])

            st.caption(f"현재 고객 번호: {df['custid'].iloc[0]}")
            st.session_state['custid'] = df['custid'].iloc[0]
            st.session_state['name'] = name
        else:
            st.warning("고객이 존재하지 않습니다!")

# ========== 탭 2 - 신규 고객 등록 & 도서 거래 ==========
with tab2:
    st.header("거래 입력 및 고객 등록")

    # 신규 고객 등록
    st.subheader("신규 고객 등록 (과제)")
    new_name = st.text_input("등록할 이름")
    new_address = st.text_input("주소")
    new_phone = st.text_input("전화번호")

    if st.button("고객 등록"):
        max_id = query("SELECT COALESCE(MAX(custid),0)+1 AS next FROM Customer")['next'][0]
        sql = f"""
        INSERT INTO Customer VALUES({max_id}, '{new_name}', '{new_address}', '{new_phone}')
        """
        con.execute(sql)
        st.success("등록 완료!")
        st.session_state['custid'] = max_id
        st.session_state['name'] = new_name

    st.markdown("---")

    # 도서 거래 입력
    st.subheader("도서 거래 입력")

    if 'custid' in st.session_state:
        st.info(f"현재 고객: {st.session_state['name']} (ID {st.session_state['custid']})")

        select_book = st.selectbox("구매 서적:", books)
        if select_book != "None":
            bookid, bookname = select_book.split(",", 1)
            price = st.number_input("금액", min_value=1)
            dt = time.strftime("%Y-%m-%d")

            if st.button("거래 입력"):
                max_oid = query("SELECT COALESCE(MAX(orderid),0)+1 AS next FROM Orders")['next'][0]
                sql = f"""
                INSERT INTO Orders VALUES({max_oid}, {st.session_state['custid']},
                {bookid}, {price}, '{dt}')
                """
                con.execute(sql)
                st.success("거래 입력 완료!")
    else:
        st.warning("먼저 고객을 조회하거나 등록하세요.")

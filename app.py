conn = duckdb.connect("madang.db")
import streamlit as st
import duckdb
import pandas as pd
import time

# -----------------------------
# 1) DuckDB 연결
# -----------------------------
DB_FILE = 'madang.db'
conn = duckdb.connect(DB_FILE)

# -----------------------------
# 2) 쿼리 실행 함수
# -----------------------------
def query(sql, fetch='df'):
    try:
        if sql.strip().upper().startswith("SELECT"):
            if fetch == 'df':
                return conn.execute(sql).fetchdf()
            else:
                return conn.execute(sql).fetchall()
        else:
            conn.execute(sql)
            conn.commit()
    except Exception as e:
        st.error(f"SQL 실행 오류: {e}")
        return None

# -----------------------------
# 3) Book 목록 불러오기
# -----------------------------
books = [None]
book_df = query("SELECT bookid, bookname FROM Book")

if book_df is not None:
    for _, row in book_df.iterrows():
        books.append(f"{row['bookid']},{row['bookname']}")

# -----------------------------
# 4) UI 시작
# -----------------------------
st.title("📚 마당 도서 관리 시스템 (DuckDB)")

tab1, tab2 = st.tabs(["고객 조회", "거래 입력 및 고객 등록"])

# -----------------------------
# TAB 1: 고객 조회
# -----------------------------
with tab1:
    st.header("고객 조회")
    search_name = st.text_input("조회할 고객명")

    if search_name:
        sql = f"""
        SELECT c.custid, c.name, b.bookname, o.orderdate, o.saleprice
        FROM Customer c
        LEFT JOIN Orders o ON c.custid = o.custid
        LEFT JOIN Book b ON o.bookid = b.bookid
        WHERE c.name = '{search_name}'
        ORDER BY o.orderdate DESC NULLS LAST
        """
        result = query(sql)

        if result is not None and not result.empty:
            # 주문 내역 중 유효한 행만 보여주기
            valid_orders = result[result['bookname'].notna()]

            st.subheader(f"'{search_name}'님의 주문 내역")
            if not valid_orders.empty:
                st.dataframe(valid_orders[['bookname', 'orderdate', 'saleprice']],
                             use_container_width=True)
            else:
                st.info("주문 내역이 없습니다.")

            # 현재 고객 정보 저장
            custid = result['custid'].iloc[0]
            st.session_state['current_custid'] = custid
            st.session_state['current_name'] = search_name
            st.caption(f"현재 고객 번호: {custid}")

        else:
            st.warning("해당 고객이 없습니다. 신규 등록하세요.")
            st.session_state['current_custid'] = None
            st.session_state['current_name'] = search_name

# -----------------------------
# TAB 2: 고객 등록 & 거래 입력
# -----------------------------
with tab2:
    st.header("거래 입력 및 고객 등록")

    current_custid = st.session_state.get("current_custid")
    current_name = st.session_state.get("current_name", "")

    # 신규 고객 등록
    st.subheader("신규 고객 등록 (과제)")
    new_name = st.text_input("등록할 이름 (필수)")
    new_address = st.text_input("주소")
    new_phone = st.text_input("전화번호 (예: 010-1234-5678)")

    if st.button("고객 등록"):
        if new_name:
            df = query("SELECT MAX(custid) AS max_id FROM Customer")
            new_custid = (df['max_id'].iloc[0] or 0) + 1

            sql = f"""
            INSERT INTO Customer VALUES (
                {new_custid}, '{new_name}', '{new_address}', '{new_phone}'
            )
            """
            query(sql)

            st.success(f"등록 완료! (고객 ID: {new_custid})")
            st.session_state['current_custid'] = new_custid
            st.session_state['current_name'] = new_name
            st.rerun()
        else:
            st.warning("이름은 필수입니다.")

    st.markdown("---")

    # 거래 입력
    st.subheader("도서 거래 입력")

    if current_custid:
        st.info(f"현재 고객: {current_name} (ID: {current_custid})")

        select_book = st.selectbox("구매 서적", books)

        if select_book and select_book != "None":
            bookid, bookname = select_book.split(",", 1)
            bookid = int(bookid)

            price = st.number_input(f"구매 금액 ({bookname})", min_value=1, step=1000)
            today = time.strftime('%Y-%m-%d')

            if st.button("거래 입력"):
                df = query("SELECT MAX(orderid) AS max_id FROM Orders")
                new_orderid = (df['max_id'].iloc[0] or 0) + 1

                sql = f"""
                INSERT INTO Orders VALUES (
                    {new_orderid}, {current_custid}, {bookid}, {price}, '{today}'
                )
                """
                query(sql)

                st.success("거래 입력 완료!")

    else:
        st.warning("먼저 고객 조회 또는 신규 등록을 해주세요.")

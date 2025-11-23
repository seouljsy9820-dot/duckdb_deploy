import streamlit as st
import duckdb
import pandas as pd
import time

# -----------------------
#  DB 연결
# -----------------------
conn = duckdb.connect("madang.db")

def query(sql, fetch="df"):
    try:
        if sql.strip().upper().startswith("SELECT"):
            if fetch == "df":
                return conn.execute(sql).fetchdf()
            else:
                return conn.execute(sql).fetchall()
        else:
            conn.execute(sql)
            conn.commit()
            return None
    except Exception as e:
        st.error(f"SQL 오류: {e}")
        return None

# -----------------------
#  초기 Book 목록 불러오기
# -----------------------
books = [None]
book_df = query("SELECT bookid, bookname FROM Book")

for _, row in book_df.iterrows():
    books.append(f"{row['bookid']},{row['bookname']}")

# -----------------------
#  UI 시작
# -----------------------
st.title("📚 마당 도서 관리 시스템 (DuckDB)")

tab1, tab2 = st.tabs(["고객 조회", "거래 입력 및 고객 등록"])

# -----------------------
#  탭 1: 고객 조회
# -----------------------
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
            st.dataframe(df[['bookname','orderdate','saleprice']], use_container_width=True)

            st.caption(f"현재 고객 번호: {df['custid'].iloc[0]}")
            st.session_state['custid'] = df['custid'].iloc[0]
            st.session_state['custname'] = name
        else:
            st.warning(f"{name} 님은 고객 DB에 없습니다.")

# -----------------------
#  탭 2: 고객 등록 + 주문 등록
# -----------------------
with tab2:
    st.header("거래 입력 및 고객 등록")
    st.subheader("신규 고객 등록")

    new_name = st.text_input("등록할 이름")
    new_addr = st.text_input("주소")
    new_phone = st.text_input("전화번호")

    if st.button("고객 등록"):
        if new_name:
            max_id_df = query("SELECT MAX(custid) AS maxid FROM Customer")
            new_id = (max_id_df['maxid'][0] or 0) + 1

            sql = f"""
            INSERT INTO Customer (custid, name, address, phone)
            VALUES ({new_id}, '{new_name}', '{new_addr}', '{new_phone}')
            """
            query(sql, fetch=None)

            st.success(f"신규 고객 '{new_name}' 등록 완료!")
            st.session_state['custid'] = new_id
            st.session_state['custname'] = new_name
        else:
            st.warning("이름은 필수입니다.")

    st.markdown("---")

    # -----------------------
    #  주문 입력
    # -----------------------
    st.subheader("도서 거래 입력")

    if 'custid' in st.session_state:
        st.info(f"현재 선택된 고객: {st.session_state['custname']} (ID: {st.session_state['custid']})")

        selected = st.selectbox("구매 서적:", books)
        if selected:
            bookid_str, bookname = selected.split(",", 1)
            price = st.number_input("판매 금액", min_value=1, step=1000)
            date = time.strftime("%Y-%m-%d")

            if st.button("거래 입력"):
                max_order = query("SELECT MAX(orderid) AS maxid FROM Orders")
                new_orderid = (max_order['maxid'][0] or 0) + 1

                sql = f"""
                INSERT INTO Orders (orderid, custid, bookid, saleprice, orderdate)
                VALUES ({new_orderid}, {st.session_state['custid']}, {bookid_str}, {price}, '{date}')
                """
                query(sql, fetch=None)

                st.success("거래 입력 완료!")
    else:
        st.warning("먼저 고객을 선택하거나 신규 고객을 등록하세요.")

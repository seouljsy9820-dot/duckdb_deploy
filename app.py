import streamlit as st
import duckdb

# DuckDB 파일 연결
con = duckdb.connect("mydb.duckdb")

st.title("🦆 DuckDB Streamlit Deploy")
st.write("아래는 DuckDB에 저장된 정보입니다:")

# -----------------------------
# 1) CUSTOMER 테이블 생성
# -----------------------------
con.execute("""
CREATE TABLE IF NOT EXISTS customer (
    id INTEGER PRIMARY KEY,
    name VARCHAR,
    phone VARCHAR,
    address VARCHAR
)
""")

# -----------------------------
# 2) BOOK 테이블 생성
# -----------------------------
con.execute("""
CREATE TABLE IF NOT EXISTS book (
    id INTEGER PRIMARY KEY,
    title VARCHAR,
    price INTEGER
)
""")

# -----------------------------
# 3) CUSTOMER 데이터 INSERT
# -----------------------------
con.execute("""
INSERT OR REPLACE INTO customer (id, name, phone, address)
VALUES (1, '장서윤', '010-7726-9820', '인하대학교')
""")

# -----------------------------
# 4) BOOK 데이터 INSERT
# -----------------------------
con.execute("""
INSERT OR REPLACE INTO book (id, title, price)
VALUES (1, '데이터베이스 시스템 개론', 20000)
""")

# -----------------------------
# 5) CUSTOMER 테이블 표로 보여주기
# -----------------------------
st.subheader("📋 Customer 테이블")
customer_df = con.execute("SELECT * FROM customer;").df()
st.dataframe(customer_df)

# -----------------------------
# 6) BOOK 테이블 표로 보여주기
# -----------------------------
st.subheader("📚 Book 테이블")
book_df = con.execute("SELECT * FROM book;").df()
st.dataframe(book_df)

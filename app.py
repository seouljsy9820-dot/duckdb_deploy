# updated

import streamlit as st
import duckdb

# DuckDB 파일 연결
con = duckdb.connect("mydb.duckdb")
# 고객 테이블 생성
con.execute("""
CREATE TABLE IF NOT EXISTS customer (
    id INTEGER PRIMARY KEY,
    name VARCHAR,
    phone VARCHAR,
    address VARCHAR
)
""")

# 책 테이블 생성
con.execute("""
CREATE TABLE IF NOT EXISTS book (
    id INTEGER PRIMARY KEY,
    title VARCHAR,
    price INTEGER
)
""")

# 고객 데이터 삽입
con.execute("""
INSERT OR IGNORE INTO customer (id, name, phone, address)
VALUES (1, '장서윤', '010-7726-9820', '인하대학교')
""")

# 책 데이터 삽입
con.execute("""
INSERT OR IGNORE INTO book (id, title, price)
VALUES (1, '데이터베이스 시스템 개론', 20000)
""")

st.title("🦆 DuckDB Streamlit Deploy")
st.write("아래는 DuckDB에 저장된 이름입니다:")

# DB에서 name 가져오기
try:
    result = con.execute("SELECT name FROM customer;").fetchall()
    if result:
        st.success(f"🌟 등록된 이름: {result[0][0]}")
    else:
        st.warning("DB에 이름이 아직 없습니다!")
except Exception as e:
    st.error("DB 접근 중 오류 발생")
    st.error(str(e))
    

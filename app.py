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
# (이미 있으면 중복 안되게 REPLACE 사용)
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
# 5) DB에서 고객 이름 불러오기
# -----------------------------
try:
    result = con.execute("SELECT name FROM customer WHERE id=1;").fetchone()

    if result:
        st.success(f"🌼 등록된 이름: {result[0]}")
    else:
        st.warning("DB에 이름이 아직 없습니다!")
except Exception as e:
    st.error("DB 조회 중 오류 발생")
    st.error(str(e))

# -----------------------------
# 6) Book 테이블 내용 보여주기
# -----------------------------
st.write("📚 저장된 Book 데이터 목록")

try:
    books = con.execute("SELECT id, title, price FROM book;").fetchall()

    if books:
        for b in books:
            st.info(f"책 ID: {b[0]} | 제목: {b[1]} | 가격: {b[2]}원")
    else:
        st.warning("현재 Book 테이블에 저장된 책이 없습니다.")
except Exception as e:
    st.error("Book 테이블 조회 중 오류 발생")
    st.error(str(e))

    

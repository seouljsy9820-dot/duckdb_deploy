
import streamlit as st
import duckdb

# DuckDB 파일 연결
con = duckdb.connect("mydb.duckdb")

st.title("🦆 DuckDB Streamlit Deploy")
st.write("아래는 DuckDB에 저장된 이름입니다:")

# DB에서 name 가져오기
try:
    result = con.execute("SELECT name FROM user;").fetchall()
    if result:
        st.success(f"🌟 등록된 이름: {result[0][0]}")
    else:
        st.warning("DB에 이름이 아직 없습니다!")
except Exception as e:
    st.error("DB 접근 중 오류 발생")
    st.error(str(e))

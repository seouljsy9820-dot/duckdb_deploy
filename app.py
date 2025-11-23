import streamlit as st
import duckdb
import pandas as pd
import time

# -----------------------------
# 🔥 DuckDB DB 연결
# -----------------------------
conn = duckdb.connect("madang.db")   # GitHub에 올린 madang.db 사용!

# -----------------------------
# 🔥 BOOK 목록 불러오기
# -----------------------------
def load_book_list():
    try:
        df = conn.execute("SELECT bookid, bookname FROM Book").fetchdf()
        books = [None]
        for _, row in df.iterrows():
            books.append(f"{row['bookid']},{row['bookname']}")
        return books
    except Exception as e:
        st.error(f"Book 테이블을 불러오는 중 오류 발생: {e}")
        return [None]

books = load_book_list()

# -----------------------------
# 🔥 Streamlit UI
# -----------------------------
st.title("📚 마당 도서 관리 시스템 (DuckDB)")

tab1, tab2 = st.tabs(["고객 조회", "거래 입력 및 고객 등록"])

# ================================
# 1️⃣ 고객 조회 탭
# ================================
with tab1:
    st.header("고객 조회")

    name = st.text_input("조회할 고객명")

    if name:
        sql = f"""
        SELECT c.custid, c.name, b.bookname, o.orderdate, o.saleprice
        FROM Customer c
        LEFT JOIN Orders o ON c.custid = o.custid
        LEFT JOIN Book b ON b.bookid = o.bookid
        WHERE c.name = '{name}'
        ORDER BY o.orderdate DESC;
        """

        try:
            df = conn.execute(sql).fetchdf()

            if not df.empty:
                st.subheader(f"'{name}' 님의 주문 내역")
                order_history = df[df["bookname"].notna()]

                if not order_history.empty:
                    st.dataframe(order_history[["bookname", "orderdate", "saleprice"]], use_container_width=True)
                else:
                    st.info("주문 내역이 없습니다.")

                custid = int(df["custid"].iloc[0])
                st.caption(f"현재 고객 번호: {custid}")

                st.session_state["current_custid"] = custid
                st.session_state["current_name"] = name

            else:
                st.warning(f"{name} 님은 고객 DB에 없습니다.")
                st.session_state["current_custid"] = None
                st.session_state["current_name"] = name

        except Exception as e:
            st.error(f"조회 중 오류 발생: {e}")


# ================================
# 2️⃣ 고객 등록 & 거래 입력 탭
# ================================
with tab2:
    st.header("거래 입력 및 고객 등록")

    # 현재 조회된 고객 정보 불러오기
    current_custid = st.session_state.get("current_custid")
    current_name = st.session_state.get("current_name", "")

    # 신규 고객 등록
    st.subheader("신규 고객 등록 (과제)")

    new_name = st.text_input("등록할 이름(필수)")
    new_addr = st.text_input("주소")
    new_phone = st.text_input("전화번호")

    if st.button("고객 등록"):
        if new_name:
            try:
                max_id = conn.execute("SELECT MAX(custid) FROM Customer").fetchone()[0]
                new_id = (max_id + 1) if max_id else 1

                conn.execute(f"""
                    INSERT INTO Customer (custid, name, address, phone)
                    VALUES ({new_id}, '{new_name}', '{new_addr}', '{new_phone}')
                """)
                conn.commit()

                st.success(f"새 고객 등록 완료! (ID: {new_id})")
                st.session_state["current_custid"] = new_id
                st.session_state["current_name"] = new_name

                st.rerun()

            except Exception as e:
                st.error(f"고객 등록 중 오류: {e}")
        else:
            st.warning("이름은 필수입니다.")

    st.markdown("---")

    # -----------------------------
    # 거래 입력
    # -----------------------------
    st.subheader("도서 거래 입력")

    if current_custid:
        st.info(f"현재 고객: {current_name} (ID: {current_custid})")

        selected_book = st.selectbox("구매 서적", books)

        if selected_book and selected_book != "None":
            bookid = int(selected_book.split(",")[0])
            price = st.number_input("구매 금액", min_value=1, step=1000)
            today = time.strftime('%Y-%m-%d')

            if st.button("거래 입력 (과제)"):
                try:
                    max_orderid = conn.execute("SELECT MAX(orderid) FROM Orders").fetchone()[0]
                    new_orderid = (max_orderid + 1) if max_orderid else 1

                    conn.execute(f"""
                        INSERT INTO Orders (orderid, custid, bookid, saleprice, orderdate)
                        VALUES ({new_orderid}, {current_custid}, {bookid}, {price}, '{today}')
                    """)
                    conn.commit()

                    st.success("거래 입력 성공!")
                except Exception as e:
                    st.error(f"거래 입력 중 오류: {e}")

    else:
        st.warning("고객 조회 탭에서 고객을 먼저 선택하세요!")

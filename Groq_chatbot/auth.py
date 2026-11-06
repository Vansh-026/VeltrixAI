
import streamlit as st
from database import init_db, register_user, login_user


def logout():
    st.session_state.clear()
    st.rerun()


def authentication():
    init_db()

    if "user" not in st.session_state:
        st.session_state.user = None

    if st.session_state.user is not None:
        return st.session_state.user

    st.title("Veltrix AI")
    st.caption("Intelligence at the Speed of Thought")

    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input(
                "Password",
                type="password"
            )
            submitted = st.form_submit_button("Login")

        if submitted:
            user = login_user(username, password)

            if user:
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Invalid username or password.")

    with register_tab:
        with st.form("register_form"):
            new_username = st.text_input("Choose username")
            new_password = st.text_input(
                "Choose password",
                type="password"
            )
            confirm_password = st.text_input(
                "Confirm password",
                type="password"
            )
            submitted = st.form_submit_button(
                "Create Account"
            )

        if submitted:
            if new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                success, message = register_user(
                    new_username,
                    new_password
                )

                if success:
                    st.success(message + " Please log in.")
                else:
                    st.error(message)

    st.stop()

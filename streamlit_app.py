# pip install plotly

# cd C:\andrmobuch\githubrepo\fire1
# streamlit run streamlit_app.py

# https://www.youtube.com/watch?v=3egaMfE9388
# Создайте Streamlit Web App с нуля (включая базу данных NoSQL + интерактивную диаграмму Sankey) 

# https://github.com/Sven-Bo?page=2&tab=repositories

# https://github.com/Sven-Bo/streamlit-income-expense-tracker  сам код

# pigar generate

import calendar  # Core Python Module
from datetime import datetime  # Core Python Module

import plotly.graph_objects as go  # pip install plotly
import streamlit as st  # pip install streamlit
from streamlit_option_menu import option_menu  # pip install streamlit-option-menu



# Конфигурация Firebase
firebaseConfig = {
      "type": st.secrets.sec.type,
      "project_id": st.secrets.sec.project_id,
      "private_key_id": st.secrets.sec.private_key_id,
      "private_key": st.secrets.sec.private_key,
      "client_email": st.secrets.sec.client_email,
      "client_id": st.secrets.sec.client_id,
      "auth_uri": st.secrets.sec.auth_uri,
      "token_uri": st.secrets.sec.token_uri,
      "auth_provider_x509_cert_url": st.secrets.sec.auth_provider_x509_cert_url,
      "client_x509_cert_url": st.secrets.sec.client_x509_cert_url,
      "universe_domain": st.secrets.sec.universe_domain
    }

firebase_url = st.secrets.sec.firebase_url


# код для фаербаз
#-----------------------------------------------------------------------------------------------

#https://blog.streamlit.io/streamlit-firestore/

#Ошибка ValueError: The default Firebase app already exists возникает, 
#когда метод initialize_app() из Firebase Admin SDK вызывается несколько 
#раз без указания уникального имени для каждого экземпляра. 
#Это часто происходит в приложениях Streamlit из-за повторных запусков, вызванных взаимодействием пользователя.

import firebase_admin
from firebase_admin import credentials, db

# Проверка инициализации Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(firebaseConfig)
    firebase_admin.initialize_app(cred, {
        'databaseURL': firebase_url
    })

class FirebaseDB:
    def __init__(self):
        """Инициализация с учетными данными Firebase."""
        self.ref = db.reference("monthly_reports")

    def create_structure_if_not_exists0(self):
        """Создать структуру, если она не существует."""
        if not self.ref.get():
            self.ref.set({
                "example_period": {
                    "incomes": 0,
                    "expenses": 0,
                    "comment": "Initial structure"
                }
            })
            
    def create_structure_if_not_exists(self):
        """Создать структуру, если она не существует."""
        if not self.ref.get():
            self.ref.set({})  # Инициализируем пустую структуру


    def insert_period0(self, period, incomes, expenses, comment):
        """Вставить отчет за определенный период."""
        self.ref.child(period).set({
            "incomes": incomes,
            "expenses": expenses,
            "comment": comment
        })
        
    def insert_period(self, period, incomes, expenses, comment):
        """Вставить отчет за определенный период."""
        self.ref.child(period).set({
            "incomes": incomes,
            "expenses": expenses,
            "comment": comment
        })
        

    def fetch_all_periods0(self):
        """Получить все периоды из базы данных."""
        res = self.ref.get()
        st.write("Raw fetched data:", res) 
        return self.ref.get()
        
    def fetch_all_periods(self):
        """Получить все периоды из базы данных."""
        return self.ref.get() or {}
        

    def get_period(self, period):
        """Получить отчет за определенный период. Возвращает None, если не найдено."""
        return self.ref.child(period).get()

#-----------------------------------------------------------------------------------------------









# Основная функция
def main():



    # -------------- SETTINGS --------------
    incomes = ["Salary", "Blog", "Other Income"]
    expenses = ["Rent", "Utilities", "Groceries", "Car", "Other Expenses", "Saving"]
    currency = "USD"
    page_title = "Income and Expense Tracker"
    page_icon = ":money_with_wings:"  # emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
    layout = "centered"
    # --------------------------------------

    st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
    st.title(page_title + " " + page_icon)

    # --- DROP DOWN VALUES FOR SELECTING THE PERIOD ---
    years = [datetime.today().year, datetime.today().year + 1]
    months = list(calendar.month_name[1:])





    # это прячет стиль приложения
    # --- HIDE STREAMLIT STYLE ---
    hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
    st.markdown(hide_st_style, unsafe_allow_html=True)


    # --- NAVIGATION MENU ---
    selected = option_menu(
        menu_title=None,
        options=["Data Entry", "Data Visualization"],
        icons=["pencil-fill", "bar-chart-fill"],  # https://icons.getbootstrap.com/
        orientation="horizontal",
    )

    db2 = FirebaseDB()
    db2.create_structure_if_not_exists()

    # --- DATABASE INTERFACE ---
    def get_all_periods0():
        items = db2.fetch_all_periods()
        periods = [item["key"] for item in items]
        return periods


    def get_all_periods():
        items = db2.fetch_all_periods()
        periods = [key for key in items.keys()]  # Извлекаем ключи
        return periods



    # --- INPUT & SAVE PERIODS ---
    if selected == "Data Entry":
        st.header(f"Data Entry in {currency}")
        with st.form("entry_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            col1.selectbox("Select Month:", months, key="month")
            col2.selectbox("Select Year:", years, key="year")

            "---"
            with st.expander("Income"):
                for income in incomes:
                    st.number_input(f"{income}:", min_value=0, format="%i", step=10, key=income)
            with st.expander("Expenses"):
                for expense in expenses:
                    st.number_input(f"{expense}:", min_value=0, format="%i", step=10, key=expense)
            with st.expander("Comment"):
                comment = st.text_area("", placeholder="Enter a comment here ...")

            "---"
            submitted = st.form_submit_button("Save Data")
            if submitted:
                period = str(st.session_state["year"]) + "_" + str(st.session_state["month"])
                incomes = {income: st.session_state[income] for income in incomes}
                expenses = {expense: st.session_state[expense] for expense in expenses}
                db2.insert_period(period, incomes, expenses, comment)
                st.success("Data saved!")


    # --- PLOT PERIODS ---
    if selected == "Data Visualization":
        st.header("Data Visualization")
        with st.form("saved_periods"):
            period = st.selectbox("Select Period:", get_all_periods())
            submitted = st.form_submit_button("Plot Period")
            if submitted:
             if period:
                # Get data from database
                period_data = db2.get_period(period)
                comment = period_data.get("comment")
                expenses = period_data.get("expenses")
                incomes = period_data.get("incomes")

                # Create metrics
                total_income = sum(incomes.values())
                total_expense = sum(expenses.values())
                remaining_budget = total_income - total_expense
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Income", f"{total_income} {currency}")
                col2.metric("Total Expense", f"{total_expense} {currency}")
                col3.metric("Remaining Budget", f"{remaining_budget} {currency}")
                st.text(f"Comment: {comment}")

                # Create sankey chart
                label = list(incomes.keys()) + ["Total Income"] + list(expenses.keys())
                source = list(range(len(incomes))) + [len(incomes)] * len(expenses)
                target = [len(incomes)] * len(incomes) + [label.index(expense) for expense in expenses.keys()]
                value = list(incomes.values()) + list(expenses.values())

                # Data to dict, dict to sankey
                link = dict(source=source, target=target, value=value)
                node = dict(label=label, pad=20, thickness=30, color="#E694FF")
                data = go.Sankey(link=link, node=node)

                # Plot it!
                fig = go.Figure(data)
                fig.update_layout(margin=dict(l=0, r=0, t=5, b=5))
                st.plotly_chart(fig, use_container_width=True)
             else:
                st.warning("Нет данных для выбранного периода.")
            else:
             st.warning("Пожалуйста, выберите период.")
             



if __name__ == "__main__":
    #external_ip = get_external_ip()
    #st.write("External IP:", external_ip)
    #main()
    a=1
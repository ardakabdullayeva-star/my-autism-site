import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# --- НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(page_title="Спектр-Помощь | Спектр-Көмек", page_icon="🧩", layout="wide")

# --- СЛОВАРЬ ПЕРЕВОДОВ ---
lang_dict = {
    "Русский": {
        "site_name": "🧩 СПЕКТР ПОМОЩИ",
        "subtitle": "Единая цифровая платформа школьного консилиума",
        "login_header": "Авторизация",
        "role_label": "Выберите вашу роль:",
        "name_label": "Фамилия специалиста:",
        "pass_label": "Пароль:",
        "login_btn": "Войти в систему",
        "logout_btn": "Выйти",
        "tab1": "📝 Обследование",
        "tab2": "📄 Протокол ИИ",
        "tab3": "📁 Архив",
        "child_id": "ФИО или ID ребенка:",
        "save_btn": "💾 Сохранить в базу",
        "ready_status": "Статус готовности:",
        "gen_report": "🤖 Сформировать Протокол",
        "roles": ["Учитель", "Психолог", "Логопед", "Дефектолог"],
        "success_save": "Данные успешно сохранены!",
        "error_pass": "Неверный пароль"
    },
    "Қазақша": {
        "site_name": "🧩 СПЕКТР КӨМЕК",
        "subtitle": "Мектеп консилиумының біріңғай сандық платформасы",
        "login_header": "Авторизация",
        "role_label": "Рөліңізді таңдаңыз:",
        "name_label": "Маманның тегі:",
        "pass_label": "Құпия сөз:",
        "login_btn": "Жүйеге кіру",
        "logout_btn": "Шығу",
        "tab1": "📝 Тексеру",
        "tab2": "📄 ИИ Хаттамасы",
        "tab3": "📁 Архив",
        "child_id": "Баланың АЖТ немесе ID:",
        "save_btn": "💾 Базаға сақтау",
        "ready_status": "Дайындық деңгейі:",
        "gen_report": "🤖 Хаттаманы дайындау",
        "roles": ["Мұғалім", "Психолог", "Логопед", "Дефектолог"],
        "success_save": "Мәліметтер сәтті сақталды!",
        "error_pass": "Құпия сөз қате"
    }
}

# --- КУСТОМНЫЙ ДИЗАЙН (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700&family=Open+Sans:wght@400;600&display=swap');
    
    .main-title {
        font-family: 'Montserrat', sans-serif;
        color: #1E3A8A;
        text-align: center;
        font-size: 55px;
        margin-bottom: 0px;
    }
    .sub-title {
        font-family: 'Open Sans', sans-serif;
        color: #4B5563;
        text-align: center;
        font-size: 20px;
        margin-bottom: 40px;
    }
    .login-box {
        background-color: #F3F4F6;
        padding: 30px;
        border-radius: 15px;
        border: 1px solid #E5E7EB;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    </style>
    """, unsafe_with_html=True)

# --- ИНИЦИАЛИЗАЦИЯ БАЗЫ ---
def init_db():
    conn = sqlite3.connect('consilium_multilang.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reports 
                 (date TEXT, role TEXT, spec_name TEXT, child_id TEXT, score INTEGER, details TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- ВЫБОР ЯЗЫКА ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3884/3884851.png", width=100)
    language = st.radio("Тіл таңдау / Выбор языка:", ["Русский", "Қазақша"])
    T = lang_dict[language]

# --- ЛОГИКА АВТОРИЗАЦИИ ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Заголовок сайта всегда сверху
st.markdown(f"<p class='main-title'>{T['site_name']}</p>", unsafe_with_html=True)
st.markdown(f"<p class='sub-title'>{T['subtitle']}</p>", unsafe_with_html=True)

if not st.session_state.logged_in:
    # Центрирование окна входа
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<div class='login-box'>", unsafe_with_html=True)
        st.subheader(T['login_header'])
        role = st.selectbox(T['role_label'], T['roles'])
        name = st.text_input(T['name_label'])
        pwd = st.text_input(T['pass_label'], type="password")
        
        if st.button(T['login_btn'], use_container_width=True):
            if pwd == "12345":
                st.session_state.logged_in = True
                st.session_state.role = role
                st.session_state.user = name
                st.rerun()
            else:
                st.error(T['error_pass'])
        st.markdown("</div>", unsafe_with_html=True)
else:
    # Если вошли — показываем рабочее место
    with st.sidebar:
        st.write(f"👤 {st.session_state.user}")
        st.write(f"🔑 {st.session_state.role}")
        if st.button(T['logout_btn']):
            st.session_state.logged_in = False
            st.rerun()

    tabs = st.tabs([T['tab1'], T['tab2'], T['tab3']])

    with tabs[0]:
        c_id = st.text_input(T['child_id'])
        st.divider()
        
        score = 0
        ans = []
        
        # --- ТЕСТЫ (Здесь вопросы на двух языках) ---
        if language == "Русский":
            if st.session_state.role == "Учитель":
                q1 = st.checkbox("Необычный визуальный контакт")
                q2 = st.checkbox("Предпочитает одиночество")
                # ... (здесь остальные вопросы)
                score = sum([q1, q2])
                ans = [f"Баллы учителя: {score}"]
        else:
            if st.session_state.role == "Мұғалім":
                q1 = st.checkbox("Ерекше көзге қарау (көз контактісінің бұзылуы)")
                q2 = st.checkbox("Жалғыз болғанды ұнатады")
                # ... (здесь вопросы на казахском)
                score = sum([q1, q2])
                ans = [f"Мұғалімнің бағалауы: {score}"]

        if st.button(T['save_btn']):
            conn = sqlite3.connect('consilium_multilang.db')
            c = conn.cursor()
            now = datetime.now().strftime("%d.%m.%Y")
            c.execute("INSERT INTO reports VALUES (?,?,?,?,?,?)", 
                      (now, st.session_state.role, st.session_state.user, c_id, score, " ".join(ans)))
            conn.commit()
            conn.close()
            st.success(T['success_save'])

    # --- ВКЛАДКИ ПРОТОКОЛ И АРХИВ ---
    with tabs[1]:
        st.subheader(T['tab2'])
        # (Логика проверки готовности специалистов как в прошлом коде)

    with tabs[2]:
        st.subheader(T['tab3'])
        conn = sqlite3.connect('consilium_multilang.db')
        df = pd.read_sql_query("SELECT * FROM reports", conn)
        st.dataframe(df, use_container_width=True)

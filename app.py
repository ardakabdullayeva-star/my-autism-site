import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime

# --- НАСТРОЙКА СТРАНИЦЫ ---
st.set_page_config(page_title="Спектр-Помощь: ПМПК", page_icon="🧩", layout="wide")

# --- ПОДКЛЮЧЕНИЕ К SUPABASE ---
@st.cache_resource
def init_connection():
    return create_engine(st.secrets["DATABASE_URL"])

engine = init_connection()

def init_db():
    with engine.begin() as conn:
        conn.execute(text('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT)'''))
        conn.execute(text('''CREATE TABLE IF NOT EXISTS teacher_reports 
                     (id SERIAL PRIMARY KEY, date TEXT, teacher_name TEXT, child_id TEXT, 
                      asd_score INTEGER, adhd_score INTEGER, details TEXT, adhd_details TEXT, notes TEXT, lang TEXT)'''))
        conn.execute(text('''CREATE TABLE IF NOT EXISTS psychologist_reports 
                     (id SERIAL PRIMARY KEY, date TEXT, psych_name TEXT, child_id TEXT, 
                      total_score INTEGER, details TEXT, notes TEXT, lang TEXT)'''))
        conn.execute(text('''CREATE TABLE IF NOT EXISTS speech_reports 
                     (id SERIAL PRIMARY KEY, date TEXT, speech_name TEXT, child_id TEXT, 
                      total_score INTEGER, details TEXT, notes TEXT, lang TEXT)'''))
        conn.execute(text('''CREATE TABLE IF NOT EXISTS defect_reports 
                     (id SERIAL PRIMARY KEY, date TEXT, defect_name TEXT, child_id TEXT, 
                      total_score INTEGER, details TEXT, notes TEXT, lang TEXT)'''))

init_db()

# --- МУЛЬТИЯЗЫЧНЫЙ СЛОВАРЬ (Сокращен для примера, структура та же) ---
# (Оставил базовые ключи для работы, текст внутри кабинетов можно вернуть из предыдущей версии, если нужно)
LANG_DATA = {
    'Русский': {
        'site_title': "ЦППМСП «Спектр-Помощь»",
        'site_subtitle': "Единая цифровая платформа психолого-педагогического консилиума",
        'tab_survey': "📝 Новое обследование",
        'tab_history': "📁 Архив записей",
        'child_label': "Код ученика",
        'date_label': "Дата обследования",
        'save_btn': "💾 Сохранить данные",
        'contacts_title': "📞 Контакты:"
    },
    'Қазақша': {
        'site_title': "«Спектр-Көмек» ПМПҚ Орталығы",
        'site_subtitle': "Психологиялық-педагогикалық консилиумның бірыңғай платформасы",
        'tab_survey': "📝 Жаңа тексеру",
        'tab_history': "📁 Жазбалар архиві",
        'child_label': "Оқушы коды",
        'date_label': "Тексеру күні",
        'save_btn': "💾 Мәліметтерді сақтау",
        'contacts_title': "📞 Байланыс мәліметтері:"
    }
}

if 'language' not in st.session_state: st.session_state.language = 'Русский'
T = LANG_DATA[st.session_state.language]

st.sidebar.title("⚙️ Настройки")
st.sidebar.radio("Тіл / Язык:", ['Русский', 'Қазақша'], key='lang_choice', 
                 on_change=lambda: setattr(st.session_state, 'language', st.session_state.lang_choice))
st.sidebar.write("---")

# ==========================================
# СИСТЕМА АВТОРИЗАЦИИ (ЕДИНАЯ)
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = ""
    st.session_state.current_role = ""

def logout():
    st.session_state.logged_in = False
    st.session_state.current_user = ""
    st.session_state.current_role = ""
    st.rerun()

if st.session_state.logged_in:
    st.sidebar.success(f"👤 {st.session_state.current_user} ({st.session_state.current_role})")
    st.sidebar.button("Выйти / Шығу", on_click=logout, use_container_width=True)

# ==========================================
# СТРАНИЦЫ
# ==========================================
def page_home():
    st.markdown(f"<h1 style='text-align: center; color: #2e6c80;'>{T['site_title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align: center;'>{T['site_subtitle']}</h4>", unsafe_allow_html=True)
    st.write("---")
    
    if not st.session_state.logged_in:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### 🔐 Вход в систему")
            role_choice = st.selectbox("Ваша должность:", ["Учитель", "Психолог", "Логопед", "Дефектолог", "Админ"])
            u_name = st.text_input("ФИО").strip()
            u_pwd = st.text_input("Пароль", type="password")
            
            if st.button("Войти", use_container_width=True, type="primary"):
                if role_choice == "Админ" and u_name.lower() in ["ардак", "директор"] and u_pwd == "Admin2026":
                    st.session_state.logged_in = True
                    st.session_state.current_user = "Абдуллаева А.Ш."
                    st.session_state.current_role = "Админ"
                    st.rerun()
                elif u_name and u_pwd:
                    with engine.connect() as conn:
                        result = conn.execute(text("SELECT password, role FROM users WHERE username = :u AND role = :r"), {"u": u_name, "r": role_choice}).fetchone()
                        if result and result[0] == u_pwd:
                            st.session_state.logged_in = True
                            st.session_state.current_user = u_name
                            st.session_state.current_role = role_choice
                            st.rerun()
                        elif result and result[0] != u_pwd:
                            st.error("Неверный пароль!")
                        else:
                            # Если пользователя нет, регистрируем
                            with engine.begin() as insert_conn:
                                insert_conn.execute(text("INSERT INTO users (username, password, role) VALUES (:u, :p, :r)"), {"u": u_name, "p": u_pwd, "r": role_choice})
                            st.session_state.logged_in = True
                            st.session_state.current_user = u_name
                            st.session_state.current_role = role_choice
                            st.success("Новый аккаунт создан! Входим...")
                            st.rerun()
                else:
                    st.warning("Заполните все поля.")
    else:
        st.success(f"Вы успешно вошли в систему как **{st.session_state.current_role}**. Выберите ваш кабинет в меню слева 👈")

def page_teacher():
    st.title("🏫 Кабинет Учителя")
    st.info("Здесь находится форма заполнения педагогического чек-листа.")
    # Тут размещается код формы учителя (как в предыдущей версии)

def page_psych():
    st.title("🧠 Кабинет Психолога")
    st.info("Здесь находится форма психолога.")
    # Тут размещается код формы психолога

def page_logo():
    st.title("🗣 Кабинет Логопеда")
    st.info("Здесь находится форма логопеда.")
    # Тут размещается код формы логопеда

def page_def():
    st.title("🎓 Кабинет Дефектолога")
    st.info("Здесь находится форма дефектолога.")
    # Тут размещается код формы дефектолога

def page_admin():
    st.title("🛡️ Панель Администратора")
    st.info("Здесь находится управление пользователями и выгрузка отчетов.")
    # Тут размещается код админ-панели

# ==========================================
# ДИНАМИЧЕСКАЯ НАВИГАЦИЯ
# ==========================================
# Базовые страницы, доступные всем
pages = {
    "Главная": [st.Page(page_home, title="Вход / Информация", icon="🏠", url_path="home")]
}

# Добавляем страницы ТОЛЬКО если пользователь авторизован, и только ДЛЯ ЕГО РОЛИ
if st.session_state.logged_in:
    role = st.session_state.current_role
    
    if role == "Учитель":
        pages["Мой Кабинет"] = [st.Page(page_teacher, title="Учитель", icon="🏫")]
    elif role == "Психолог":
        pages["Мой Кабинет"] = [st.Page(page_psych, title="Психолог", icon="🧠")]
    elif role == "Логопед":
        pages["Мой Кабинет"] = [st.Page(page_logo, title="Логопед", icon="🗣")]
    elif role == "Дефектолог":
        pages["Мой Кабинет"] = [st.Page(page_def, title="Дефектолог", icon="🎓")]
    elif role == "Админ":
        pages["Управление"] = [st.Page(page_admin, title="Администратор", icon="🛡️")]

# Запуск навигации
pg = st.navigation(pages)
pg.run()

import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# --- НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(page_title="Спектр-Помощь | Спектр-Көмек", page_icon="🧩", layout="wide")

# --- СЛОВАРЬ ПЕРЕВОДОВ ИНТЕРФЕЙСА ---
lang_dict = {
    "Русский": {
        "site_name": "🧩 СПЕКТР ПОМОЩИ",
        "subtitle": "Единая цифровая платформа школьного консилиума",
        "login_header": "Авторизация в системе",
        "role_label": "Выберите вашу роль:",
        "name_label": "Фамилия специалиста:",
        "pass_label": "Пароль:",
        "login_btn": "Войти в систему",
        "logout_btn": "Выйти из системы",
        "tab1": "📝 Обследование",
        "tab2": "📄 Итоговый протокол ИИ",
        "tab3": "📁 Архив записей",
        "child_id": "Введите ФИО или ID ребенка:",
        "save_btn": "💾 Сохранить в архив консилиума",
        "ready_status": "Статус готовности данных:",
        "gen_report": "🤖 Сгенерировать Протокол и Рекомендации ИИ",
        "roles": ["Учитель", "Психолог", "Логопед", "Дефектолог"],
        "success_save": "Ваша часть обследования успешно сохранена!",
        "error_pass": "Неверный пароль!",
        "auth_warning": "Пожалуйста, авторизуйтесь в системе для получения доступа к тестам.",
        "db_empty": "В базе данных пока нет записей.",
        "missing_data": "Для генерации отчета не хватает данных от: ",
        "all_ready": "✅ Все данные собраны. ИИ готов к формированию протокола.",
        "ai_conclusion": "ЗАКЛЮЧЕНИЕ ИИ-ПОМОЩНИКА:",
        "ai_score": "Общий суммарный балл: ",
        "ai_risk": "Уровень риска: ",
        "ai_rec_label": "РЕКОМЕНДАЦИИ:",
        "download_btn": "📥 Скачать Итоговый Протокол (.txt)"
    },
    "Қазақша": {
        "site_name": "🧩 СПЕКТР КӨМЕК",
        "subtitle": "Мектеп консилиумының біріңғай сандық платформасы",
        "login_header": "Жүйеге кіру",
        "role_label": "Рөліңізді таңдаңыз:",
        "name_label": "Маманның тегі:",
        "pass_label": "Құпия сөз:",
        "login_btn": "Жүйеге кіру",
        "logout_btn": "Жүйеден шығу",
        "tab1": "📝 Тексеру",
        "tab2": "📄 ИИ Қорытынды Хаттамасы",
        "tab3": "📁 Жазбалар архиві",
        "child_id": "Баланың АЖТ немесе ID енгізіңіз:",
        "save_btn": "💾 Консилиум архивіне сақтау",
        "ready_status": "Мәліметтердің дайындық деңгейі:",
        "gen_report": "🤖 Хаттаманы және ИИ ұсыныстарын дайындау",
        "roles": ["Мұғалім", "Психолог", "Логопед", "Дефектолог"],
        "success_save": "Тексеру мәліметтеріңіз сәтті сақталды!",
        "error_pass": "Құпия сөз қате!",
        "auth_warning": "Тесттерге қол жеткізу үшін жүйеге кіріңіз.",
        "db_empty": "Мәліметтер базасы бос.",
        "missing_data": "Есепті дайындау үшін мына мамандардың деректері жеткіліксіз: ",
        "all_ready": "✅ Барлық мәліметтер жиналды. ИИ хаттаманы дайындауға дайын.",
        "ai_conclusion": "ЖАСАНДЫ ИНТЕЛЛЕКТ КӨМЕКШІСІНІҢ ҚОРЫТЫНДЫСЫ:",
        "ai_score": "Жалпы жиынтық балл: ",
        "ai_risk": "Қауіп деңгейі: ",
        "ai_rec_label": "ҰСЫНЫСТАР:",
        "download_btn": "📥 Қорытынды хаттаманы жүктеу (.txt)"
    }
}

# --- КУСТОМНЫЙ ДИЗАЙН (CSS) ---
st.markdown("""
    <style>
    .main-title {
        color: #1E3A8A;
        text-align: center;
        font-size: 50px;
        margin-bottom: 5px;
        font-weight: 700;
    }
    .sub-title {
        color: #4B5563;
        text-align: center;
        font-size: 18px;
        margin-bottom: 35px;
    }
    .login-box {
        background-color: #F9FAFB;
        padding: 35px;
        border-radius: 15px;
        border: 1px solid #E5E7EB;
    }
    </style>
    """, unsafe_with_html=True)

# --- ИНИЦИАЛИЗАЦИЯ БАЗЫ ---
def init_db():
    conn = sqlite3.connect('school_consilium_multilang_v1.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reports 
                 (date TEXT, role TEXT, spec_name TEXT, child_id TEXT, score INTEGER, details TEXT)''')
    conn.commit()
    conn.close()

init_db()

REQUIRED_ROLES_RU = ["Учитель", "Психолог", "Логопед", "Дефектолог"]

# --- ВЫБОР ЯЗЫКА ---
with st.sidebar:
    language = st.radio("Тіл / Язык:", ["Русский", "Қазақша"])
    T = lang_dict[language]

role_mapping = {
    T["roles"][0]: "Учитель",
    T["roles"][1]: "Психолог",
    T["roles"][2]: "Логопед",
    T["roles"][3]: "Дефектолог"
}

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Заголовок сверху
st.markdown(f"<div class='main-title'>{T['site_name']}</div>", unsafe_with_html=True)
st.markdown(f"<div class='sub-title'>{T['subtitle']}</div>", unsafe_with_html=True)

if not st.session_state.logged_in:
    # Центрирование формы входа
    col1, col2, col3 = st.columns([1, 1.3, 1])
    with col2:
        st.markdown("<div class='login-box'>", unsafe_with_html=True)
        st.markdown(f"<h3 style='text-align: center;'>{T['login_header']}</h3>", unsafe_with_html=True)
        role_input = st.selectbox(T['role_label'], T['roles'])
        name_input = st.text_input(T['name_label'])
        pwd_input = st.text_input(T['pass_label'], type="password")
        
        if st.button(T['login_btn'], use_container_width=True, type="primary"):
            if pwd_input == "12345":
                st.session_state.logged_in = True
                st.session_state.role = role_mapping[role_input]
                st.session_state.role_display = role_input
                st.session_state.user = name_input
                st.rerun()
            else:
                st.error(T['error_pass'])
        st.markdown("</div>", unsafe_with_html=True)
else:
    with st.sidebar:
        st.write("---")
        st.markdown(f"**👤 {T['name_label']}** {st.session_state.user}")
        st.markdown(f"**🔑 {T['role_label']}** {st.session_state.role_display}")
        if st.button(T['logout_btn'], use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    tabs = st.tabs([T['tab1'], T['tab2'], T['tab3']])

    # --- ВКЛАДКА 1: ОБСЛЕДОВАНИЕ ---
    with tabs[0]:
        child_id = st.text_input(T['child_id'], "Иванов Иван")
        st.write("---")
        
        score = 0
        details = ""

        if language == "Русский":
            if st.session_state.role == "Учитель":
                st.subheader("Скрининг-анкета для классного руководителя")
                q = [
                    st.checkbox("Необычный визуальный контакт (взгляд «сквозь» человека)"),
                    st.checkbox("Предпочитает играть или находиться в одиночестве"),
                    st.checkbox("Не понимает личных границ (близость/касания)"),
                    st.checkbox("Редко делится радостями или достижениями"),
                    st.checkbox("Использует в речи цитаты или повторы (эхолалия)"),
                    st.checkbox("Речь звучит «роботизированно» или официально"),
                    st.checkbox("Не понимает сарказм, шутки (буквальное понимание)"),
                    st.checkbox("Трудности с инициацией разговора / просьбой"),
                    st.checkbox("Остро реагирует на шумы (звонок, столовая)"),
                    st.checkbox("Необычные пищевые привычки"),
                    st.checkbox("Повторяющиеся движения (взмахи, раскачивания)"),
                    st.checkbox("Стресс при изменении распорядка или маршрута")
                ]
                score = sum(q)
                details = f"Педагогические маркеры: {score}/12"

            elif st.session_state.role == "Психолог":
                st.subheader("Скрининг-тест психолога (общий)")
                p = [
                    st.checkbox("Удерживание взгляда кратковременное/отсутствует"),
                    st.checkbox("Отсутствие разделенного внимания (не показывает пальцем)"),
                    st.checkbox("Несоответствующий эмоциональный отклик"),
                    st.checkbox("Трудности определения эмоций по картинкам"),
                    st.checkbox("Речь только для просьб (нет спонтанного общения)"),
                    st.checkbox("Невыполнение простых инструкций с первого раза"),
                    st.checkbox("Монотонная или слишком громкая интонация"),
                    st.checkbox("Буквальное понимание переносного смысла"),
                    st.checkbox("Трудности объединения предметов в группы (обобщение)"),
                    st.checkbox("Ошибки в логике (Четвертый лишний)"),
                    st.checkbox("Нарушение причинно-следственных связей"),
                    st.checkbox("Наличие навязчивых движений (стереотипии)"),
                    st.checkbox("Сенсорный поиск или избегание (трогает всё / боится грязи)"),
                    st.checkbox("Высокий уровень тревожности при переменах")
                ]
                score = sum(p)
                details = f"Психологические маркеры: {score}/14"

            elif st.session_state.role == "Логопед":
                st.subheader("Логопедический скрининг")
                l = [
                    st.checkbox("Эхолалия (повторение фраз)"),
                    st.checkbox("Путаница местоимений (Я/Он)"),
                    st.checkbox("Нарушение просодики (ритм/темп)"),
                    st.checkbox("Отсутствие коммуникативной инициативы"),
                    st.checkbox("Трудности понимания многоступенчатых инструкций"),
                    st.checkbox("Нарушение прагматики речи (поддержание диалога)")
                ]
                score = sum(l)
                details = f"Речевые дефициты: {score}/6"

            elif st.session_state.role == "Дефектолог":
                st.subheader("Дефектологический скрининг")
                d = [
                    st.checkbox("Трудности имитации простых действий"),
                    st.checkbox("Слабая зрительно-моторная координация"),
                    st.checkbox("Непонимание пространственных предлогов (над/под/за)"),
                    st.checkbox("Трудности переключения между задачами"),
                    st.checkbox("Нарушение узнавания сенсорных эталонов (форма/цвет)"),
                    st.checkbox("Трудности логического обобщения")
                ]
                score = sum(d)
                details = f"Когнитивные дефициты: {score}/6"
        
        else:
            if st.session_state.role == "Учитель":
                st.subheader("Сынып жетекшісіне арналған скрининг-сауалнама")
                q = [
                    st.checkbox("Ерекше көзге қарау контактісі (адамның «ішінен өткізіп» қарау)"),
                    st.checkbox("Жалғыз ойнауды немесе жалғыз болуды қалайды"),
                    st.checkbox("Жеке шекараны түсінбейді (жақындық/жанасу)"),
                    st.checkbox("Қуаныштарын немесе жетістіктерін сирек бөліседі"),
                    st.checkbox("Сөйлеуде цитаталарды немесе қайталауларды қолданады (эхолалия)"),
                    st.checkbox("Сөйлеуі «роботтандырылған» немесе тым ресми естіледі"),
                    st.checkbox("Әзілді, мысқылды түсінбейді (сөзді тура мағынада түсіну)"),
                    st.checkbox("Әңгіме бастау / өтініш білдіру қиындықтары"),
                    st.checkbox("Шуылға (қоңырау, асхана) қатты сезімталдық танытады"),
                    st.checkbox("Ерекше тамақтану әдеттері бар"),
                    st.checkbox("Қайталанатын қозғалыстар (қол бұлғау, тербелу)"),
                    st.checkbox("Күн тәртібі немесе бағыт өзгерген кездегі стресс")
                ]
                score = sum(q)
                details = f"Педагогикалық маркерлер: {score}/12"

            elif st.session_state.role == "Психолог":
                st.subheader("Психологтың скринингтік тесті (жалпы)")
                p = [
                    st.checkbox("Көз контактісін сақтау қысқа мерзімді немесе мүлдем жоқ"),
                    st.checkbox("Бөлінген назардың болмауы (саусағымен көрсетпейді)"),
                    st.checkbox("Сәйкес келмейтін эмоционалды жауап"),
                    st.checkbox("Суреттер бойынша эмоцияларды анықтау қиындығы"),
                    st.checkbox("Тек өтініштер үшін сөйлеу (өздігінен қарым-қатынас жоқ)"),
                    st.checkbox("Қарапайым нұсқауларды бірінші реттен орындамау"),
                    st.checkbox("Монотонды немесе тым қатты дауыс интонациясы"),
                    st.checkbox("Ауыспалы мағынаны тура мағынада түсіну"),
                    st.checkbox("Заттарды топтарға біріктіру қиындығы (жалпылау)"),
                    st.checkbox("Логикадағы қателер (Төртіншісі артық)"),
                    st.checkbox("Себеп-салдарлық байланыстардың бұзылуы"),
                    st.checkbox("Еріксіз қайталанатын қозғалыстардың болуы (стереотипия)"),
                    st.checkbox("Сенсорлық ізденіс немесе қашу (бәрін ұстау / кірден қорқу)"),
                    st.checkbox("Өзгерістер кезіндегі жоғары мазасыздық деңгейі")
                ]
                score = sum(p)
                details = f"Психологиялық маркерлер: {score}/14"

            elif st.session_state.role == "Логопед":
                st.subheader("Логопедиялық скрининг")
                l = [
                    st.checkbox("Эхолалия (фразаларды қайталау)"),
                    st.checkbox("Есімдіктерді шатастыру (Мен/Ол)"),
                    st.checkbox("Просодиканың бұзылуы (ырғақ/қарқын)"),
                    st.checkbox("Коммуникативтік бастаманың болмауы"),
                    st.checkbox("Көп сатылы нұсқауларды түсіну қиындығы"),
                    st.checkbox("Сөйлеу прагматикасының бұзылуы (диалогты қолдау)")
                ]
                score = sum(l)
                details = f"Сөйлеу тапшылығы: {score}/6"

            elif st.session_state.role == "Дефектолог":
                st.subheader("Дефектологиялық скрининг")
                d = [
                    st.checkbox("Қарапайым әрекеттерге еліктеу (имитация) қиындықтары"),
                    st.checkbox("Нашар көру-моторлық үйлесімділігі"),
                    st.checkbox("Кеңістіктік септіктерді түсінбеу (үстінде/астында/артында)"),
                    st.checkbox("Тапсырмалар арасында ауысу қиындықтары"),
                    st.checkbox("Сенсорлық эталондарды (пішін/түс) танудың бұзылуы"),
                    st.checkbox("Логикалық жалпылау қиындықтары")
                ]
                score = sum(d)
                details = f"Когнитивті тапшылық: {score}/6"

        if st.button(T['save_btn'], use_container_width=True):
            conn = sqlite3.connect('school_consilium_multilang_v1.db')
            c = conn.cursor()
            now = datetime.now().strftime("%d.%m.%Y %H:%M")
            c.execute("INSERT INTO reports VALUES (?, ?, ?, ?, ?, ?)", 
                      (now, st.session_state.role, st.session_state.user, child_id, score, details))
            conn.commit()
            conn.close()
            st.success(T['success_save'])

    # --- ВКЛАДКА 2: ИТОГОВЫЙ ПРОТОКОЛ ИИ ---
    with tabs[1]:
        st.subheader(T['ready_status'])
        conn = sqlite3.connect('school_consilium_multilang_v1.db')
        all_data = pd.read_sql_query("SELECT * FROM reports", conn)
        conn.close()
        
        if not all_data.empty:
            target_child = st.selectbox(T['child_id'], all_data['child_id'].unique(), key="child_select")
            child_results = all_data[all_data['child_id'] == target_child]
            
            roles_submitted = child_results['role'].unique()
            missing = [r for r in REQUIRED_ROLES_RU if r not in roles_submitted]
            
            cols = st.columns(len(REQUIRED_ROLES_RU))
            for i, r in enumerate(REQUIRED_ROLES_RU):
                role_display_name = T["roles"][i]
                cols[i].metric(role_display_name, "✅" if r in roles_submitted else "❌")

            if not missing:
                st.success(T['all_ready'])
                if st.button(T['gen_report'], use_container_width=True, type="primary"):
                    total_score = child_results['score'].sum()
                    
                    if language == "Русский":
                        if total_score >= 20:
                            risk_level = "ВЫСОКИЙ"
                            advice = "Необходима консультация ПМПК. Рекомендовано обучение по адаптированной программе (АОП), тьюторское сопровождение и коррекционные занятия не менее 5 раз в неделю."
                        elif total_score >= 10:
                            risk_level = "СРЕДНИЙ"
                            advice = "Рекомендована адаптация образовательной среды: визуальные опоры, сенсорная разгрузка. Индивидуальные занятия со школьными специалистами."
                        else:
                            risk_level = "НИЗКИЙ"
                            advice = "Выраженных признаки не обнаружены. Рекомендовано плановое педагогическое наблюдение."
                    else:
                        if total_score >= 20:
                            risk_level = "ЖОҒАРЫ"
                            advice = "ПМПК консультациясы қажет. Бейімделген білім беру бағдарламасы (БББ), тьюторлық қолдау және аптасына кемінде 5 рет түзету сабақтары ұсынылады."
                        elif total_score >= 10:
                            risk_level = "ОРТАША"
                            advice = "Білім беру ортасын бейімдеу ұсынылады: визуалды тіректер, сенсорлық жеңілдету. Мектеп мамандарымен жеке түзету сабақтары."
                        else:
                            risk_level = "TӨMEH"
                            advice = "Айқын белгілер анықталған жоқ. Жоспарлы педагогикалық бақылау ұсынылады."

                    if language == "Русский":
                        final_report = f"ИТОГОВЫЙ ПРОТОКОЛ КОНСИЛИУМА: {target_child}\nДата: {datetime.now().strftime('%d.%m.%Y')}\n----------------------------------------\n"
                        for _, row in child_results.iterrows():
                            final_report += f"- {row['role']} ({row['spec_name']}): {row['details']}\n"
                        final_report += f"\n----------------------------------------\n{T['ai_conclusion']}\n{T['ai_score']}{total_score}\n{T['ai_risk']}{risk_level}\n\n{T['ai_rec_label']}\n{advice}\n"
                    else:
                        final_report = f"КОНСИЛИУМНЫҢ ҚОРЫТЫНДЫ ХАТТАМАСЫ: {target_child}\nКүні: {datetime.now().strftime('%d.%m.%Y')}\n----------------------------------------\n"
                        for _, row in child_results.iterrows():
                            role_kz = T["roles"][REQUIRED_ROLES_RU.index(row['role'])]
                            final_report += f"- {role_kz} ({row['spec_name']}): {row['details']}\n"
                        final_report += f"\n----------------------------------------\n{T['ai_conclusion']}\n{T['ai_score']}{total_score}\n{T['ai_risk']}{risk_level}\n\n{T['ai_rec_label']}\n{advice}\n"
                    
                    st.text_area(T['tab2'], final_report, height=350)
                    st.download_button(
                        label=T['download_btn'],
                        data=final_report.encode('utf-16'),
                        file_name=f"Protocol_{target_child}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
            else:
                missing_translated = [T["roles"][REQUIRED_ROLES_RU.index(r)] for r in missing]
                st.warning(f"{T['missing_data']}{', '.join(missing_translated)}")
        else:
            st.info(T['db_empty'])

    # --- ВКЛАДКА 3: АРХИВ ---
    with tabs[2]:
        st.subheader(T['tab3'])
        conn = sqlite3.connect('school_consilium_multilang_v1.db')
        df = pd.read_sql_query("SELECT date, role, spec_name, child_id, score, details FROM reports", conn)
        conn.close()
        st.dataframe(df, use_container_width=True)

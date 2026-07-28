import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime

# --- НАСТРОЙКА СТРАНИЦЫ (Должна быть первой командой) ---
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

# --- МУЛЬТИЯЗЫЧНЫЙ СЛОВАРЬ ---
LANG_DATA = {
    'Русский': {
        'site_title': "ЦППМСП «Спектр-Помощь»",
        'site_subtitle': "Единая цифровая платформа психолого-педагогического консилиума",
        'tab_survey': "📝 Новое обследование",
        'tab_report': "📋 Комплексный отчет",
        'tab_history': "📁 Архив записей",
        'child_label': "Код ученика (для анонимности)",
        'child_placeholder': "Например: 1А01",
        'date_label': "Дата обследования",
        'save_btn': "💾 Сохранить данные",
        'auth_name': "Ваша Фамилия и Инициалы",
        'auth_pwd': "Ваш личный пароль",
        'auth_btn': "Войти в кабинет",
        'extra_notes_label': "✍️ Дополнительные экспертные наблюдения:",
        'placeholder_notes': "Введите информацию...",
        'contacts_title': "📞 Контакты:",

        # --- УЧИТЕЛЬ (РУС) ---
        'teach_title': "🏫 Педагогический чек-лист оценки развития ребёнка",
        'teach_secs': [
            "1️⃣ Особенности коммуникации и речи", "2️⃣ Социальное взаимодействие", "3️⃣ Поведение и учебный процесс", "4️⃣ Сенсорные реакции",
            "1️⃣ Невнимательность (Дефицит внимания)", "2️⃣ Гиперактивность (Избыточная моторная активность)", "3️⃣ Импульсивность (Неумение тормозить реакции)"
        ],
        'teach_q': [
            ["Игнорирование обращений: ребенок не отзывается на свое имя, хотя со слухом все в порядке.", "Эхолалия: бесконтрольное повторение чужих слов, фраз или цитат из мультиков вместо спонтанной речи.", "Буквальное понимание: невосприимчивость к метафорам, сарказму, скрытому смыслу или шуткам.", "Специфический тон: монотонная, излишне правильная («роботизированная») или слишком взрослая речь.", "Трудности с диалогом: ребенок может долго говорить на интересную тему, но не слушать собеседника."],
            ["Избегание зрительного контакта: ребенок смотрит «сквозь» учителя или быстро отводит глаза.", "Проблемы с границами: полное игнорирование личной дистанции либо, наоборот, резкое отстранение от прикосновений.", "Одиночество на переменах: ребенок не играет с одноклассниками, держится в стороне или просто наблюдает.", "Трудности с правилами играх: непонимание негласных социальных норм, неумение делиться или ждать очереди.", "Нетипичная мимика: выражение лица часто не соответствует ситуации или остается абсолютно маской."],
            ["Стереотипии (стимминг): повторяющиеся движения тела (взмахи руками как крыльями, раскачивание на стуле).", "Протест против изменений: паника или агрессия при смене расписания, замене учителя или пересаживании.", "Узкие интересы: фанатичная увлеченность одной темой (динозавры, схемы) в ущерб остальным урокам.", "Особый порядок: стремление раскладывать карандаши или тетради в строгой последовательности; сильная тревога."],
            ["Гиперчувствительность: ребенок закрывает уши руками при звонке, криках на перемене или звуке стульев.", "Избирательность в еде: в школьной столовой ест только строго определенные продукты (например, сухой хлеб).", "Дискомфорт от одежды: постоянные попытки снять школьную форму, срезать ярлыки из-за их «колкости»."],
            ["Быстрая отвлекаемость: ребенок реагирует на любой шорох за окном или скрип двери, теряя нить урока.", "Проблемы с инструкциями: не может выполнить задание из 3-4 шагов (забывает начало, пока дослушивает).", "Постоянная потеря вещей: регулярно теряет карандаши, ластики, тетради, забывает в классе вещи.", "Ошибки по «глупости»: из-за небрежности пропускает буквы, знаки препинания или цифры, хотя правила знает.", "Избегание умственных усилий: всеми силами оттягивает начало выполнения сложных, монотонных заданий."],
            ["Физическая неусидчивость: ребенок постоянно крутится, сползает под парту, закидывает ноги.", "Постоянные движения руками: вертит в руках ручку, ломает карандаши, ковыряет заусенцы, стучит по столу.", "Бесцельное хождение: может встать посреди урока, чтобы подойти к шкафу, потому что не в силах сидеть.", "«Шумное» поведение: часто производит много лишних звуков (скрипит стулом, роняет предметы, громко вздыхает).", "Проблемы на переменах: бегает на пределе скорости, врезается в людей и углы, не умеет играть спокойно."],
            ["Выкрикивание с места: отвечает до того, как учитель договорил вопрос. Не может дождаться, пока вызовут.", "Перебивание: постоянно встревает в разговоры учителя с другими детьми или прерывает одноклассников.", "Неумение ждать очереди: в играх или в столовой пытается всегда быть первым, бурно протестует в очереди.", "Слабый самоконтроль: сначала делает или говорит, а потом думает. Может взять чужую вещь без спроса.", "Вспыльчивость: легко расстраивается, бурно реагирует на проигрыш в игре или замечание, плачет или злится."]
        ],

        # --- ПСИХОЛОГ (РУС) ---
        'psych_title': "🧠 Кабинет Психолога",
        'psych_secs': ["Блок 1: Эмоционально-волевая сфера и тревожность", "Блок 2: Когнитивная сфера", "Блок 3: Социализация", "Блок 4: Мотивационный компонент"],
        'psych_q': [
            ["Высокий уровень базовой тревожности (боится сделать ошибку).", "Резкие перепады настроения без видимой внешней причины.", "Вспышки гнева на сверстников или аутоагрессия.", "Наличие выраженных страхов (боязнь отвечать у доски, паника).", "Ребенок мгновенно сдается при малейшей неудаче."],
            ["Ребенок продуктивен только первые 10–15 минут, затем утомление.", "Трудности с кратковременным запоминанием.", "С трудом переключается с одного алгоритма мышления на другой.", "Путает «право/лево», «верх/низ», зеркально пишет буквы."],
            ["Трудности в принятии школьных правил и позиции взрослого.", "Ребенок является объектом насмешек, буллинга или игнорирования.", "Не понимает эмоций других людей, не сопереживает."],
            ["Полное отсутствие учебной мотивации.", "Ребенок постоянно транслирует установки: «Я глупый», «У меня не получится»."]
        ],

        # --- ЛОГОПЕД (РУС) ---
        'logo_title': "🗣 Кабинет Логопеда",
        'logo_secs': ["Блок 1: Звукопроизношение", "Блок 2: Слоговая структура", "Блок 3: Фонематические процессы", "Блок 4: Связная речь", "Блок 5: Темп речи"],
        'logo_q': [
            ["Нарушения звукопроизношения (сигматизм, ротацизм).", "Нарушения артикуляционной моторики."],
            ["Искажение слоговой структуры (пропуски слогов, перестановки)."],
            ["Нарушение фонематического слуха (не различает Б-П, З-С).", "Трудности звукового анализа и синтеза."],
            ["Бедный словарный запас.", "Аграмматизмы (ошибки в согласовании).", "Нарушение связной речи (не может пересказать текст)."],
            ["Наличие запинок, заикания, слишком быстрый или медленный темп."]
        ],

        # --- ДЕФЕКТОЛОГ (РУС) ---
        'def_title': "🎓 Кабинет Дефектолога",
        'def_secs': ["Блок 1: Обучаемость", "Блок 2: ВПФ", "Блок 3: Элементарные знания", "Блок 4: Академические навыки"],
        'def_q': [
            ["Низкая обучаемость (не принимает помощь взрослого).", "Несформированность игровой/учебной деятельности."],
            ["Нарушение зрительного и слухового гнозиса.", "Дефициты конструирования (не может собрать картинку).", "Особенности мышления (трудности классификации)."],
            ["Незнание сенсорных эталонов (путает цвета, формы).", "Нарушение пространственных ориентировок (вчера/сегодня)."],
            ["Трудности формирования навыка чтения.", "Нарушения письма (пропуски гласных, зеркальное написание).", "Нарушения счета (не соотносит цифру с количеством)."]
        ]
    },
    'Қазақша': {
        'site_title': "«Спектр-Көмек» ПМПҚ Орталығы",
        'site_subtitle': "Психологиялық-педагогикалық консилиумның бірыңғай платформасы",
        'tab_survey': "📝 Жаңа тексеру",
        'tab_report': "📋 Кешенді есеп",
        'tab_history': "📁 Жазбалар архиві",
        'child_label': "Оқушы коды (анонимділік үшін)",
        'child_placeholder': "Мысалы: 1А01",
        'date_label': "Тексеру күні",
        'save_btn': "💾 Мәліметтерді сақтау",
        'auth_name': "Тегіңіз бен аты-жөніңіз",
        'auth_pwd': "Жеке құпия сөзіңіз",
        'auth_btn': "Кабинетке кіру",
        'extra_notes_label': "✍️ Қосымша сараптамалық бақылаулар:",
        'placeholder_notes': "Ақпаратты енгізіңіз...",
        'contacts_title': "📞 Байланыс мәліметтері:",

        # --- УЧИТЕЛЬ (ҚАЗ) ---
        'teach_title': "🏫 Бала дамуын бағалаудың педагогикалық чек-лисі",
        'teach_secs': [
            "1️⃣ Коммуникация", "2️⃣ Әлеуметтік өзара әрекеттесу", "3️⃣ Мінез-құлық", "4️⃣ Сенсорлық реакциялар",
            "1️⃣ Зейінсіздік", "2️⃣ Гиперактивтілік", "3️⃣ Импульсивтілік"
        ],
        'teach_q': [
            ["Өтініштерді елемеу: бала өз атына жауап бермейді.", "Эхолалия: басқалардың сөздерін бақылаусыз қайталау.", "Тура мағынада түсіну: астарлы ойды немесе әзілдерді қабылдамау.", "Ерекше тон: тым дұрыс («роботталған») сөйлеу мәнері.", "Диалог құру қиындықтары: сұхбаттасушыны тыңдамайды."],
            ["Көзбен байланыстан қашу.", "Шекаралармен мәселелер: жеке қашықтықты елемеу.", "Үзілістегі жалғыздық.", "Ойын ережелерімен қиындықтар.", "Типтік емес мимика."],
            ["Стереотипиялар (қайталанатын дене қимылдары).", "Өзгерістерге қарсылық.", "Тар қызығушылықтар (тек бір тақырыпқа қызығу).", "Ерекше тәртіп: заттарды қатаң ретпен орналастыру."],
            ["Аса сезімталдық (қатты дыбыстардан қорқу).", "Тамақ талғау.", "Киімнен жайсыздық (затбелгілерді кесіп тастау)."],
            ["Тез алаңдаушылық.", "Нұсқаулармен мәселелер (3-4 қадамдық тапсырманы орындай алмау).", "Заттарды үнемі жоғалту.", "«Ақымақ» қателер (ұқыпсыздықтан).", "Ақыл-ой күшінен қашу."],
            ["Физикалық шыдамсыздық.", "Қолдың үнемі қозғалыста болуы.", "Мақсатсыз жүру.", "«Шулы» мінез-құлық.", "Үзілістегі мәселелер."],
            ["Орындан айқайлау.", "Сөзді бөлу.", "Кезекті күте алмау.", "Өзін-өзі бақылаудың төмендігі.", "Ашуланшақтық."]
        ],

        # --- ПСИХОЛОГ (ҚАЗ) ---
        'psych_title': "🧠 Психолог кабинеті",
        'psych_secs': ["1-блок: Эмоционалды ая", "2-блок: Когнитивті ая", "3-блок: Әлеуметтену", "4-блок: Мотивация"],
        'psych_q': [
            ["Жоғары базалық мазасыздық деңгейі.", "Эмоционалды лабильдік.", "Агрессия көріністері.", "Үрей мен фобиялар.", "Фрустрацияға төзімділіктің төмендігі."],
            ["Психикалық үрдістердің тез сарқылуы.", "Естің ерекшеліктері (қысқа мерзімді ес тапшылығы).", "Ойлаудың ригидтілігі.", "Кеңістікті бағдарлай алмау."],
            ["Ережелерді қабылдамау.", "Ұжымнан шеттетілу.", "Эмпатияның төмендігі."],
            ["Мектепке дезадаптация.", "Өзін-өзі бағалаудың төмендігі."]
        ],

        # --- ЛОГОПЕД (ҚАЗ) ---
        'logo_title': "🗣 Логопед кабинеті",
        'logo_secs': ["1-блок: Дыбыстың айтылуы", "2-блок: Буындық құрылым", "3-блок: Фонематикалық үрдістер", "4-блок: Байланыстырып сөйлеу", "5-блок: Сөйлеу қарқыны"],
        'logo_q': [
            ["Дыбыстың айтылуындағы бұзылыстар.", "Артикуляциялық моториканың бұзылуы."],
            ["Сөздің буындық құрылымын бұрмалау."],
            ["Фонематикалық есту қабілетінің бұзылуы.", "Дыбыстық талдау қиындықтары."],
            ["Сөздік қордың жұтаңдығы.", "Аграмматизмдер.", "Байланыстырып сөйлеудің бұзылуы."],
            ["Тұтығу, сөйлеудегі кідірістер."]
        ],

        # --- ДЕФЕКТОЛОГ (ҚАЗ) ---
        'def_title': "🎓 Дефектолог кабинеті",
        'def_secs': ["1-блок: Оқытылу деңгейі", "2-блок: Жоғары психикалық функциялар", "3-блок: Қарапайым түсініктер", "4-блок: Академиялық дағдылар"],
        'def_q': [
            ["Төмен оқытылу деңгейі.", "Оқу/ойын әрекетінің қалыптаспауы."],
            ["Көру және есту гнозисінің бұзылуы.", "Конструкциялық праксис дефициті.", "Ойлау ерекшеліктері."],
            ["Сенсорлық эталондарды білмеу.", "Уақыт пен кеңістікті бағдарлай алмау."],
            ["Оқу дағдысының қиындықтары.", "Жазудың бұзылыстары.", "Есептеу дағдысының бұзылуы."]
        ]
    }
}

# --- ГЛОБАЛЬНЫЕ НАСТРОЙКИ ЯЗЫКА ---
if 'language' not in st.session_state: st.session_state.language = 'Русский'
T = LANG_DATA[st.session_state.language]

st.sidebar.title("⚙️ Баптаулар / Настройки")
st.sidebar.radio("Тіл / Язык:", ['Русский', 'Қазақша'], key='lang_choice', 
                 on_change=lambda: setattr(st.session_state, 'language', st.session_state.lang_choice))
st.sidebar.write("---")

# ==========================================
# ФУНКЦИЯ УНИВЕРСАЛЬНОЙ АВТОРИЗАЦИИ
# ==========================================
def login_block(role):
    logged_key = f"logged_in_{role}"
    user_key = f"user_{role}"
    
    if logged_key not in st.session_state: st.session_state[logged_key] = False
    if user_key not in st.session_state: st.session_state[user_key] = ""
    
    if not st.session_state[logged_key]:
        st.markdown(f"<h2 style='text-align: center;'>Вход: {role}</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form(key=f"auth_{role}"):
                u_name = st.text_input(T['auth_name']).strip()
                u_pwd = st.text_input(T['auth_pwd'], type="password")
                submit = st.form_submit_button(T['auth_btn'], use_container_width=True, type="primary")
                
                if submit:
                    if role == "Админ":
                        if (u_name.lower() == "ардак" or u_name.lower() == "директор") and u_pwd == "Admin2026":
                            st.session_state[logged_key] = True
                            st.session_state[user_key] = "Абдуллаева А.Ш."
                            st.rerun()
                        else: st.error("Неверный логин или пароль!")
                    elif u_name and u_pwd:
                        with engine.connect() as conn:
                            result = conn.execute(text("SELECT password, role FROM users WHERE username = :u AND role = :r"), {"u": u_name, "r": role}).fetchone()
                            if result:
                                if result[0] == u_pwd:
                                    st.session_state[logged_key] = True
                                    st.session_state[user_key] = u_name
                                    st.rerun()
                                else: st.error("Неверный пароль!")
                            else:
                                user_exists = conn.execute(text("SELECT role FROM users WHERE username = :u"), {"u": u_name}).fetchone()
                                if user_exists:
                                    st.error(f"Пользователь зарегистрирован как {user_exists[0]}! Перейдите в правильный кабинет слева.")
                                else:
                                    with engine.begin() as insert_conn:
                                        insert_conn.execute(text("INSERT INTO users (username, password, role) VALUES (:u, :p, :r)"), {"u": u_name, "p": u_pwd, "r": role})
                                    st.session_state[logged_key] = True
                                    st.session_state[user_key] = u_name
                                    st.rerun()
                    else:
                        st.warning("Заполните все поля.")
        return False
    else:
        st.sidebar.success(f"👤 {st.session_state[user_key]} ({role})")
        if st.sidebar.button("Выйти / Шығу", key=f"logout_{role}", use_container_width=True):
            st.session_state[logged_key] = False
            st.session_state[user_key] = ""
            st.rerun()
        return True

# ==========================================
# СТРАНИЦЫ ПРИЛОЖЕНИЯ
# ==========================================
def page_home():
    st.markdown(f"<h1 style='text-align: center; color: #2e6c80;'>{T['site_title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align: center;'>{T['site_subtitle']}</h4>", unsafe_allow_html=True)
    st.write("---")
    st.info("👈 **Пожалуйста, выберите ваш личный кабинет в боковом меню слева.**")
    st.write("---")
    st.markdown(f"👥 **{T['contacts_title']}**")
    st.markdown("""
    * **ФИО:** Абдуллаева Ардақ Шығайқызы
    * **Телефон / WhatsApp:** +77787954638
    * **Email:** ardak.abdullayeva@aktau7.edu.kz
    """)

def render_history_tab(table_name, name_col, role_title):
    try:
        df = pd.read_sql_query(f"SELECT date as \"Дата\", {name_col} as \"ФИО Специалиста\", child_id as \"Код ребенка\", notes as \"Комментарий\" FROM {table_name} ORDER BY id DESC", engine)
        st.dataframe(df, use_container_width=True) if not df.empty else st.info(f"Нет записей в архиве {role_title}.")
    except Exception as e: st.error(f"Ошибка загрузки архива: {e}")

def page_teacher():
    if login_block("Учитель"):
        st.title(T['teach_title'])
        tabs = st.tabs([T['tab_survey'], T['tab_history']])
        with tabs[0]:
            c_col1, c_col2 = st.columns(2)
            child_name = c_col1.text_input(T['child_label'], placeholder=T['child_placeholder'])
            survey_date = c_col2.date_input(T['date_label'], datetime.now())
            st.write("---")
            asd_score, adhd_score = 0, 0
            st.markdown("## 🧩 РАС")
            for i in range(0, 4):
                st.markdown(f"#### {T['teach_secs'][i]}")
                for idx, q in enumerate(T['teach_q'][i]):
                    if st.checkbox(q, key=f"t_q_ras_{i}_{idx}"): asd_score += 1
            st.markdown("<br><hr><br>", unsafe_allow_html=True)
            st.markdown("## ⚡ СДВГ")
            for i in range(4, 7):
                st.markdown(f"#### {T['teach_secs'][i]}")
                for idx, q in enumerate(T['teach_q'][i]):
                    if st.checkbox(q, key=f"t_q_adhd_{i}_{idx}"): adhd_score += 1
            st.write("---")
            extra_notes = st.text_area(T['extra_notes_label'], placeholder=T['placeholder_notes'])
            if st.button(T['save_btn'], use_container_width=True, type="primary"):
                if child_name:
                    with engine.begin() as conn:
                        conn.execute(text("INSERT INTO teacher_reports (date, teacher_name, child_id, asd_score, adhd_score, details, adhd_details, notes, lang) VALUES (:d, :n, :c, :a, :ad, 'РАС', 'СДВГ', :not, :l)"),
                                     {"d": survey_date.strftime("%d.%m.%Y"), "n": st.session_state["user_Учитель"], "c": child_name, "a": asd_score, "ad": adhd_score, "not": extra_notes, "l": st.session_state.language})
                    st.success(f"🎉 Данные сохранены!")
                else: st.error("Пожалуйста, введите код ребенка!")
        with tabs[1]: render_history_tab("teacher_reports", "teacher_name", "Учителя")

def page_psych():
    if login_block("Психолог"):
        st.title(T['psych_title'])
        tabs = st.tabs([T['tab_survey'], T['tab_history']])
        with tabs[0]:
            c_col1, c_col2 = st.columns(2)
            child_name = c_col1.text_input(T['child_label'], placeholder=T['child_placeholder'])
            survey_date = c_col2.date_input(T['date_label'], datetime.now())
            st.write("---")
            total_score = 0
            for i, sec in enumerate(T['psych_secs']):
                st.markdown(f"### {sec}")
                for idx, q in enumerate(T['psych_q'][i]):
                    if st.checkbox(q, key=f"p_q_{i}_{idx}"): total_score += 1
            st.write("---")
            extra_notes = st.text_area(T['extra_notes_label'], placeholder=T['placeholder_notes'])
            if st.button(T['save_btn'], use_container_width=True, type="primary"):
                if child_name:
                    with engine.begin() as conn:
                        conn.execute(text("INSERT INTO psychologist_reports (date, psych_name, child_id, total_score, details, notes, lang) VALUES (:d, :n, :c, :s, 'Психология', :not, :l)"),
                                     {"d": survey_date.strftime("%d.%m.%Y"), "n": st.session_state["user_Психолог"], "c": child_name, "s": total_score, "not": extra_notes, "l": st.session_state.language})
                    st.success(f"🎉 Данные сохранены!")
                else: st.error("Введите код ребенка!")
        with tabs[1]: render_history_tab("psychologist_reports", "psych_name", "Психолога")

def page_logo():
    if login_block("Логопед"):
        st.title(T['logo_title'])
        tabs = st.tabs([T['tab_survey'], T['tab_history']])
        with tabs[0]:
            c_col1, c_col2 = st.columns(2)
            child_name = c_col1.text_input(T['child_label'], placeholder=T['child_placeholder'])
            survey_date = c_col2.date_input(T['date_label'], datetime.now())
            st.write("---")
            total_score = 0
            for i, sec in enumerate(T['logo_secs']):
                st.markdown(f"### {sec}")
                for idx, q in enumerate(T['logo_q'][i]):
                    if st.checkbox(q, key=f"l_q_{i}_{idx}"): total_score += 1
            st.write("---")
            extra_notes = st.text_area(T['extra_notes_label'], placeholder=T['placeholder_notes'])
            if st.button(T['save_btn'], use_container_width=True, type="primary"):
                if child_name:
                    with engine.begin() as conn:
                        conn.execute(text("INSERT INTO speech_reports (date, speech_name, child_id, total_score, details, notes, lang) VALUES (:d, :n, :c, :s, 'Логопедия', :not, :l)"),
                                     {"d": survey_date.strftime("%d.%m.%Y"), "n": st.session_state["user_Логопед"], "c": child_name, "s": total_score, "not": extra_notes, "l": st.session_state.language})
                    st.success(f"🎉 Данные сохранены!")
                else: st.error("Введите код ребенка!")
        with tabs[1]: render_history_tab("speech_reports", "speech_name", "Логопеда")

def page_def():
    if login_block("Дефектолог"):
        st.title(T['def_title'])
        tabs = st.tabs([T['tab_survey'], T['tab_history']])
        with tabs[0]:
            c_col1, c_col2 = st.columns(2)
            child_name = c_col1.text_input(T['child_label'], placeholder=T['child_placeholder'])
            survey_date = c_col2.date_input(T['date_label'], datetime.now())
            st.write("---")
            total_score = 0
            for i, sec in enumerate(T['def_secs']):
                st.markdown(f"### {sec}")
                for idx, q in enumerate(T['def_q'][i]):
                    if st.checkbox(q, key=f"d_q_{i}_{idx}"): total_score += 1
            st.write("---")
            extra_notes = st.text_area(T['extra_notes_label'], placeholder=T['placeholder_notes'])
            if st.button(T['save_btn'], use_container_width=True, type="primary"):
                if child_name:
                    with engine.begin() as conn:
                        conn.execute(text("INSERT INTO defect_reports (date, defect_name, child_id, total_score, details, notes, lang) VALUES (:d, :n, :c, :s, 'Дефектология', :not, :l)"),
                                     {"d": survey_date.strftime("%d.%m.%Y"), "n": st.session_state["user_Дефектолог"], "c": child_name, "s": total_score, "not": extra_notes, "l": st.session_state.language})
                    st.success(f"🎉 Данные сохранены!")
                else: st.error("Введите код ребенка!")
        with tabs[1]: render_history_tab("defect_reports", "defect_name", "Дефектолога")

def page_admin():
    if login_block("Админ"):
        st.title("🛡️ Панель Администратора")
        admin_tabs = st.tabs(["📊 Контроль и Специфика", "📋 Формирование ПМПК", "🗄️ База Данных"])
        
        with admin_tabs[0]:
            st.subheader("👥 Зарегистрированные специалисты")
            users_df = pd.read_sql_query('SELECT username as "ФИО Специалиста", role as "Роль / Кабинет", password as "Текущий Пароль" FROM users', engine)
            st.dataframe(users_df, use_container_width=True)
            if not users_df.empty:
                user_to_del = st.selectbox("Кого удалить из системы?", users_df["ФИО Специалиста"].tolist())
                if st.button(f"❌ Удалить доступ для {user_to_del}", type="primary"):
                    with engine.begin() as conn:
                        conn.execute(text("DELETE FROM users WHERE username = :u"), {"u": user_to_del})
                    st.success(f"Специалист удален!")
                    st.rerun()

        with admin_tabs[1]:
            st.subheader("📋 Генерация комплексного отчета ПМПК")
            try:
                t_kids = pd.read_sql_query("SELECT DISTINCT child_id FROM teacher_reports", engine)['child_id'].tolist()
                p_kids = pd.read_sql_query("SELECT DISTINCT child_id FROM psychologist_reports", engine)['child_id'].tolist()
                l_kids = pd.read_sql_query("SELECT DISTINCT child_id FROM speech_reports", engine)['child_id'].tolist()
                d_kids = pd.read_sql_query("SELECT DISTINCT child_id FROM defect_reports", engine)['child_id'].tolist()
                all_kids = sorted(list(set(t_kids + p_kids + l_kids + d_kids)))
            except: all_kids = []
            
            if all_kids:
                selected_kid = st.selectbox("🎯 Выберите код ученика:", all_kids)
                if st.button("🤖 Сформировать заключение ПМПК", type="primary"):
                    st.write("---")
                    st.markdown(f"### 📄 Сводная экспертная оценка по ученику: **{selected_kid}**")
                    t_rep = pd.read_sql_query(text("SELECT * FROM teacher_reports WHERE child_id = :c ORDER BY id DESC LIMIT 1"), engine, params={"c": selected_kid})
                    p_rep = pd.read_sql_query(text("SELECT * FROM psychologist_reports WHERE child_id = :c ORDER BY id DESC LIMIT 1"), engine, params={"c": selected_kid})
                    score_table = []
                    if not t_rep.empty:
                        score_table.append({"Сфера": "РАС (Педагог)", "Баллы": f"{t_rep.iloc[0]['asd_score']} / 19", "Специалист": t_rep.iloc[0]['teacher_name']})
                        score_table.append({"Сфера": "СДВГ (Педагог)", "Баллы": f"{t_rep.iloc[0]['adhd_score']} / 15", "Специалист": t_rep.iloc[0]['teacher_name']})
                    if not p_rep.empty:
                        score_table.append({"Сфера": "Психология", "Баллы": f"{p_rep.iloc[0]['total_score']} / 14", "Специалист": p_rep.iloc[0]['psych_name']})
                    st.table(pd.DataFrame(score_table)) if score_table else st.warning("Недостаточно данных.")
            else: st.info("В базе пока нет заполненных анкет.")
            
        with admin_tabs[2]:
            st.write("Сырые данные базы (Архив всех таблиц)")
            raw_tabs = st.tabs(["Учителя", "Психологи"])
            with raw_tabs[0]: st.dataframe(pd.read_sql_query("SELECT * FROM teacher_reports", engine), use_container_width=True)
            with raw_tabs[1]: st.dataframe(pd.read_sql_query("SELECT * FROM psychologist_reports", engine), use_container_width=True)

# ==========================================
# ЗАПУСК НАВИГАЦИИ (STREAMLIT 1.36+)
# ==========================================
pg = st.navigation({
    "Информация": [
        st.Page(page_home, title="Главная страница", icon="🏠", url_path="home")
    ],
    "Кабинеты специалистов": [
        st.Page(page_teacher, title="Учитель", icon="🏫", url_path="teacher"),
        st.Page(page_psych, title="Психолог", icon="🧠", url_path="psychologist"),
        st.Page(page_logo, title="Логопед", icon="🗣", url_path="speech_therapist"),
        st.Page(page_def, title="Дефектолог", icon="🎓", url_path="defectologist")
    ],
    "Управление": [
        st.Page(page_admin, title="Администратор", icon="🛡️", url_path="admin")
    ]
})

pg.run()

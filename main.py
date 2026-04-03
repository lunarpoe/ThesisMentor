import io
import os
import traceback
import streamlit as st
from dotenv import load_dotenv

# Импорты ваших модулей
from core.parser import ThesisParser
from core.critic import CriticManager
from core.generator_giga import GeneratorManager

# Настройка страницы
st.set_page_config(page_title="LISA AI Thesis Critic", layout="wide")
load_dotenv("config.env")

# Кешируем инициализацию, чтобы она не происходила при каждом нажатии кнопки
@st.cache_resource
def init_systems():
    print("Инициализация систем...")
    try:
        parser = ThesisParser()
        critic = CriticManager()
        generator = GeneratorManager()
        generator.add_manual_rules()
        return parser, critic, generator
    except Exception as e:
        st.error(f"Критическая ошибка инициализации: {e}")
        return None, None, None

parser, critic, generator = init_systems()

st.title("🎓 LISA AI: Анализ тезисов")

# Загрузка файла
uploaded_file = st.file_uploader("Выберите файл диссертации (.docx)", type=["docx"])

if uploaded_file is not None:
    if st.button("Запустить анализ"):
        with st.spinner("Анализируем документ..."):
            try:
                # Читаем файл в поток
                file_stream = io.BytesIO(uploaded_file.read())

                # 1. Парсинг
                graph = parser.parse(file_stream)
                
                # 2. Критика
                errors = critic.run_all(graph)
                
                # 3. Рекомендации
                recommendations = generator.generate_recommendations_from_errors(errors, graph)

                # --- ОТОБРАЖЕНИЕ РЕЗУЛЬТАТОВ ---
                st.success("Анализ завершен!")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("⚠️ Найденные ошибки")
                    if errors:
                        for err in errors:
                            st.warning(f"**{err.get('type', 'Ошибка')}**: {err.get('message', 'Без описания')}")
                    else:
                        st.write("Ошибок не обнаружено.")

                with col2:
                    st.subheader("💡 Рекомендации")
                    for rec in recommendations:
                        st.info(rec)

                # Техническая информация
                with st.expander("Детали структуры документа"):
                    st.write(f"Количество узлов: {len(graph.get('nodes', {}))}")
                    sections = [n["title"] for n in graph.get("nodes", {}).values() if n.get("type") == "SECTION"]
                    st.write("Обнаруженные разделы:", sections)

            except Exception as e:
                st.error(f"Ошибка при обработке: {e}")
                st.code(traceback.format_exc())

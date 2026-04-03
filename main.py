import main
import streamlit as st
import asyncio

# Настройка внешнего вида страницы
st.set_page_config(
    page_title="AI Рецензент ВКР",
    # page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Проверка структуры ВКР")
st.markdown(
    "Загрузите файл вашей работы в формате `.docx`, чтобы модель-критик проверила "
    "соответствие структуры и содержания практических глав тексту введения."
)

# для отладочной информации
with st.sidebar:
    st.header(" Отладка парсера")
    st.info("структура документа после обработки.")
    debug_container = st.empty()

# 3. Основная область загрузки файла
uploaded_file = st.file_uploader("Выберите файл .docx", type=["docx"])

if uploaded_file is not None:
    # Кнопка для старта
    if st.button("Запустить анализ", type="primary"):
        
        with st.spinner("Анализируем документ... Это может занять несколько секунд."):
            try:
                # ВЫЗОВ АНАЛИЗА (Заменили requests на прямой вызов из main)
                # Передаем uploaded_file вместо несуществующего user_input
                data = asyncio.run(main.analyze_document(uploaded_file))
                
                # Извлекаем результаты из ответа (как в твоем исходном коде)
                results = data.get("results", {})
                errors = results.get("errors", [])
                recommendations = results.get("recommendations", [])
                    
                st.success("Анализ успешно завершен!")
                    
                # Вывод отладочной информации в сайдбар
                with debug_container.container():
                    st.metric("Всего узлов в графе", results.get("nodes_count", 0))
                    st.subheader("Распознанные разделы:")
                    for sec in results.get("detected_sections", []):
                        st.text(f"🔹 {sec['title']}")

                # Разделение экрана на две колонки (Твой дизайн)
                col1, col2 = st.columns(2)
                    
                with col1:
                    st.header("Заключение Критика")
                    if not errors:
                        st.success("Отлично! Структурных ошибок не найдено.")
                    else:
                        for i, err in enumerate(errors):
                            with st.expander(f"Недочет #{i+1} (Узел: {err['node_id'][:8]}...)", expanded=True):
                                st.error(err['description'])
                                st.caption(f"Статус: {err.get('error_status', 'Найдено')}")

                with col2:
                    st.header("Советы LISA AI")
                    if not recommendations:
                        st.info("Загрузите файл для получения рекомендаций.")
                    else:
                        for i, rec in enumerate(recommendations):
                            is_struct = rec.get("is_structural", False)
                            icon = "🏗️" if is_struct else "✍️"

                            with st.expander(f"{icon} Рекомендация #{i+1}", expanded=True):
                                text_content = rec.get('suggestion', '')

                                if "Исправленный текст:" in text_content:
                                    parts = text_content.split("Исправленный текст:")
                                    st.markdown(f"**Анализ:** {parts

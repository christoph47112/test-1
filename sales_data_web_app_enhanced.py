
import pandas as pd
import streamlit as st
from io import BytesIO

# Title and Sidebar
st.set_page_config(page_title="Abverkaufsmengen Berechnung", layout="wide")
st.title("Berechnung der ∅ Abverkaufsmengen pro Woche von Werbeartikeln zu Normalpreisen")

st.sidebar.title("Optionen")
language = st.sidebar.selectbox("Sprache", ["Deutsch"])
texts = {
    "Deutsch": {
        "upload_prompt": "Bitte laden Sie Ihre Datei hoch (Excel oder CSV)",
        "file_processing": "Die Datei wird verarbeitet...",
        "error_missing_columns": "Fehler: Die Datei muss die Spalten 'Artikel', 'Menge' und 'Name' enthalten.",
        "results": "Ergebnisse",
        "download": "Laden Sie die Ergebnisse herunter",
        "example_file": "Laden Sie eine Beispieldatei herunter",
        "instructions": "Anleitung anzeigen",
        "instructions_text": '''
### Anleitung zur Nutzung dieser App
1. Laden Sie Ihre Verkaufsdaten als Excel- oder CSV-Datei hoch.
   - Die Datei muss mindestens die Spalten **'Artikel', 'Menge' und 'Name'** enthalten.
2. Überprüfen Sie die Ergebnisse in der Tabelle.
3. Laden Sie die Ergebnisse als Excel-Datei herunter.
4. Wenn Sie eine Beispieldatei benötigen, können Sie diese über die Option in der Seitenleiste herunterladen.
'''
    }
}
text = texts[language]

# Example File
example_data = {
    "Artikel": ["001", "002", "003"],
    "Name": ["Milch 1L", "Butter 250g", "Käse 500g"],
    "Menge": [100, 150, 200]
}
example_df = pd.DataFrame(example_data)
example_file = BytesIO()
example_df.to_excel(example_file, index=False, engine='openpyxl')
example_file.seek(0)
st.sidebar.download_button(label=text["example_file"], data=example_file, file_name="beispiel_abverkauf.xlsx")

# Display Instructions
if st.sidebar.button(text["instructions"]):
    st.markdown(text["instructions_text"])

# File Uploader
uploaded_file = st.file_uploader(text["upload_prompt"], type=["xlsx", "csv"])

if uploaded_file:
    with st.spinner(text["file_processing"]):
        try:
            # File Handling
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.ExcelFile(uploaded_file).parse(0)

            # Validate required columns
            required_columns = {"Artikel", "Name", "Menge"}
            if not required_columns.issubset(df.columns):
                st.error(text["error_missing_columns"])
            else:
                # Calculate average sales
                average_sales = df.groupby('Artikel')['Menge'].mean().reset_index()
                average_sales.rename(columns={'Menge': 'Durchschnittliche Menge pro Woche'}, inplace=True)

                # Merge with original data for sorting
                sorted_sales = df[['Artikel', 'Name']].drop_duplicates().merge(
                    average_sales, on='Artikel', how='left'
                )

                # Display Results
                st.subheader(text["results"])
                st.dataframe(sorted_sales)

                # Optimized Performance: Allow result caching
                @st.cache_data
                def convert_df(df):
                    output = BytesIO()
                    df.to_excel(output, index=False, engine='openpyxl')
                    output.seek(0)
                    return output

                output_file = convert_df(sorted_sales)
                st.download_button(text["download"], data=output_file, file_name="ergebnisse.xlsx")
        except Exception as e:
            st.error(f"Fehler bei der Verarbeitung der Datei: {e}")

st.markdown("---")
st.markdown(
    "⚠️ **Hinweis:** Diese Anwendung speichert keine Daten und hat keinen Zugriff auf Ihre Dateien. "
    "Alle Verarbeitungen erfolgen lokal auf Ihrem Gerät oder auf dem temporären Streamlit-Server."
)

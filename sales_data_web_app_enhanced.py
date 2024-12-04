import pandas as pd
import streamlit as st
from io import BytesIO

# Title and Sidebar
st.set_page_config(page_title="Abverkaufsmengen Berechnung", layout="wide")
st.title("Berechnung der ∅ Abverkaufsmengen pro Woche von Werbeartikeln zu Normalpreisen")

# Sidebar options
language = st.sidebar.selectbox("Sprache", ["Deutsch"])
texts = {
    "Deutsch": {
        "upload_prompt": "Bitte laden Sie Ihre Datei hoch (Excel oder CSV)",
        "file_processing": "Die Datei wird verarbeitet...",
        "error_missing_columns": "Fehler: Die Datei muss die Spalten 'Artikel', 'Woche', 'Menge' und 'Name' enthalten.",
        "results": "Ergebnisse",
        "download": "Laden Sie die Ergebnisse herunter",
        "example_file": "Laden Sie eine Beispieldatei herunter",
        "export_format": "Wählen Sie das Exportformat:",
        "recommended": "Empfohlen: Excel",
        "instructions": "Anleitung",
        "instructions_text": '''
### Anleitung zur Nutzung dieser App
1. Bereiten Sie Ihre Abverkaufsdaten vor:
   - Die Datei muss die Spalten **'Artikel', 'Woche', 'Menge' (in Stück) und 'Name'** enthalten.
   - Speichern Sie die Datei im Excel- oder CSV-Format.
2. Laden Sie Ihre Datei hoch:
   - Nutzen Sie die Schaltfläche „Durchsuchen“ und wählen Sie Ihre Datei aus.
3. Überprüfen Sie die berechneten Ergebnisse:
   - Die App zeigt die durchschnittlichen Abverkaufsmengen pro Woche an.
4. Wählen Sie das gewünschte Exportformat:
   - Standardmäßig wird Excel empfohlen.
5. Laden Sie die Ergebnisse herunter:
   - Nutzen Sie die Schaltfläche „Laden Sie die Ergebnisse herunter“, um die berechneten Daten zu speichern.
'''
    }
}
text = texts[language]

# Example File with realistic data
example_data = {
    "Artikel": ["001", "001", "001", "002", "002", "002", "003", "003", "003"],
    "Name": ["Milch 1L", "Milch 1L", "Milch 1L", "Butter 250g", "Butter 250g", "Butter 250g", "Käse 500g", "Käse 500g", "Käse 500g"],
    "Woche": [1, 2, 3, 1, 2, 3, 1, 2, 3],
    "Menge": [100, 120, 110, 150, 140, 160, 200, 210, 190]
}
example_df = pd.DataFrame(example_data)
example_file = BytesIO()
example_df.to_excel(example_file, index=False, engine='openpyxl')
example_file.seek(0)

# Initialize session state for toggle
if "show_app" not in st.session_state:
    st.session_state["show_app"] = False

# Display Anleitung or App based on toggle
if st.session_state["show_app"]:
    st.sidebar.markdown(text["instructions_text"])
    button_text = "Nur Anleitung anzeigen"
else:
    st.sidebar.markdown(text["instructions_text"])
    button_text = "Modul benutzen und Anleitung angezeigt bekommen"

if st.sidebar.button(button_text):
    st.session_state["show_app"] = not st.session_state["show_app"]

# Example file download
st.sidebar.download_button(
    label=text["example_file"],
    data=example_file,
    file_name="beispiel_abverkauf.xlsx",
    key="example_download"
)

# Display App functionality if toggle is active
if st.session_state["show_app"]:
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
                required_columns = {"Artikel", "Woche", "Menge", "Name"}
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

                    # Export Format Selection
                    st.subheader(text["export_format"])
                    export_format = st.radio(
                        "Wählen Sie ein Format für den Export:",
                        ["Excel (empfohlen)", "CSV"],
                        index=0
                    )
                    st.markdown(f"**{text['recommended']}**")

                    # Export Results
                    if export_format == "Excel (empfohlen)":
                        @st.cache_data
                        def convert_to_excel(df):
                            output = BytesIO()
                            df.to_excel(output, index=False, engine='openpyxl')
                            output.seek(0)
                            return output

                        output_file = convert_to_excel(sorted_sales)
                        st.download_button(text["download"], data=output_file, file_name="ergebnisse.xlsx")
                    elif export_format == "CSV":
                        @st.cache_data
                        def convert_to_csv(df):
                            return df.to_csv(index=False).encode('utf-8')

                        output_file = convert_to_csv(sorted_sales)
                        st.download_button(text["download"], data=output_file, file_name="ergebnisse.csv")
            except Exception as e:
                st.error(f"Fehler bei der Verarbeitung der Datei: {e}")

    # Credits and Disclaimer
    st.markdown("---")
    st.markdown("⚠️ **Hinweis:** Diese Anwendung speichert keine Daten und hat keinen Zugriff auf Ihre Dateien.")
    st.markdown("🌟 **Erstellt von Christoph R. Kaiser mit Hilfe von Künstlicher Intelligenz.**")

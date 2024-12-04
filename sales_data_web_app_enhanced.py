import pandas as pd
import streamlit as st
from io import BytesIO

# Title and Page Layout
st.set_page_config(page_title="Berechnung der ∅ Abverkaufsmengen", layout="wide")
st.title("Berechnung der ∅ Abverkaufsmengen pro Woche von Werbeartikeln zu Normalpreisen")

# Initialize session state for toggle functionality
if "show_module" not in st.session_state:
    st.session_state["show_module"] = False

# Sidebar: Sprachauswahl
language = st.sidebar.selectbox("Sprache", ["Deutsch", "Englisch"])

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
        "instructions_text": """
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
"""
    },
    "Englisch": {
        "upload_prompt": "Please upload your file (Excel or CSV)",
        "file_processing": "Processing the file...",
        "error_missing_columns": "Error: The file must contain the columns 'Artikel', 'Woche', 'Menge', and 'Name'.",
        "results": "Results",
        "download": "Download the results",
        "example_file": "Download an example file",
        "export_format": "Select the export format:",
        "recommended": "Recommended: Excel",
        "instructions": "Instructions",
        "instructions_text": """
### How to use this app
1. Prepare your sales data:
   - The file must contain the columns **'Artikel', 'Woche', 'Menge' (in units), and 'Name'**.
   - Save the file in Excel or CSV format.
2. Upload your file:
   - Use the “Browse” button to select your file.
3. Check the calculated results:
   - The app will show the average weekly sales per article.
4. Choose the desired export format:
   - By default, Excel is recommended.
5. Download the results:
   - Use the “Download the results” button to save the calculated data.
"""
    },
}

text = texts[language]

# Navigation
page = st.sidebar.radio("Navigation", ["Hauptseite", text["instructions"]])

# Hauptseite anzeigen
if page == "Hauptseite":
    st.subheader("Willkommen auf der Hauptseite")
    st.write("Hier können Sie Ihre Abverkaufsdaten hochladen und analysieren.")

# Anleitung anzeigen
elif page == text["instructions"]:
    # Anleitung
    st.markdown(text["instructions_text"])

    # Button mit sofortiger Funktionalität
    if st.button(
        "Nur Anleitung anzeigen" if st.session_state["show_module"] else "Modul benutzen und Anleitung anzeigen"
    ):
        st.session_state["show_module"] = not st.session_state["show_module"]

    # Beispieldatei Download
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

    st.download_button(
        label=text["example_file"],
        data=example_file,
        file_name="beispiel_abverkauf.xlsx"
    )

    # Modul anzeigen, falls aktiviert
    if st.session_state["show_module"]:
        st.subheader("Modul")
        uploaded_file = st.file_uploader(text["upload_prompt"], type=["xlsx", "csv"])

        if uploaded_file:
            with st.spinner(text["file_processing"]):
                try:
                    if uploaded_file.name.endswith('.csv'):
                        df = pd.read_csv(uploaded_file)
                    else:
                        df = pd.ExcelFile(uploaded_file).parse(0)

                    required_columns = {"Artikel", "Woche", "Menge", "Name"}
                    if not required_columns.issubset(df.columns):
                        st.error(text["error_missing_columns"])
                    else:
                        average_sales = df.groupby('Artikel')['Menge'].mean().reset_index()
                        average_sales.rename(columns={'Menge': 'Durchschnittliche Menge pro Woche'}, inplace=True)
                        sorted_sales = df[['Artikel', 'Name']].drop_duplicates().merge(
                            average_sales, on='Artikel', how='left'
                        )
                        st.subheader(text["results"])
                        st.dataframe(sorted_sales)

                        export_format = st.radio(
                            text["export_format"],
                            ["Excel (empfohlen)", "CSV"],
                            index=0
                        )

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

        st.markdown("---")
        st.markdown("⚠️ **Hinweis:** Diese Anwendung speichert keine Daten und hat keinen Zugriff auf Ihre Dateien.")
        st.markdown("🌟 **Erstellt von Christoph R. Kaiser mit Hilfe von Künstlicher Intelligenz.**")

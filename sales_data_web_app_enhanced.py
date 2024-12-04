import pandas as pd
import streamlit as st
from io import BytesIO

# Title and Page Layout
st.set_page_config(page_title="Berechnung der ∅ Abverkaufsmengen", layout="wide")
st.title("Berechnung der ∅ Abverkaufsmengen pro Woche von Werbeartikeln zu Normalpreisen")

# Beispieldatei vorbereiten
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

# Sidebar: Navigation und Beispieldatei
st.sidebar.header("Menü")
st.sidebar.radio("Navigation", ["Hauptseite", "Anleitung"], key="navigation")
st.sidebar.download_button(
    label="Beispieldatei herunterladen",
    data=example_file,
    file_name="beispiel_abverkauf.xlsx"
)

# Navigation auswerten
if st.session_state.navigation == "Hauptseite":
    # Datei-Uploader
    uploaded_file = st.file_uploader("Bitte laden Sie Ihre Datei hoch (Excel oder CSV)", type=["xlsx", "csv"])

    if uploaded_file:
        with st.spinner("Die Datei wird verarbeitet..."):
            try:
                # Datei lesen
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.ExcelFile(uploaded_file).parse(0)

                # Spalten prüfen
                required_columns = {"Artikel", "Woche", "Menge", "Name"}
                if not required_columns.issubset(df.columns):
                    st.error("Fehler: Die Datei muss die Spalten 'Artikel', 'Woche', 'Menge' und 'Name' enthalten.")
                else:
                    # Durchschnitt berechnen
                    average_sales = df.groupby('Artikel')['Menge'].mean().reset_index()
                    average_sales.rename(columns={'Menge': 'Durchschnittliche Menge pro Woche'}, inplace=True)

                    # Ergebnisse anzeigen
                    st.subheader("Ergebnisse")
                    st.dataframe(average_sales)

                    # Exportformat auswählen
                    export_format = st.radio(
                        "Wählen Sie das Exportformat:",
                        ["Excel (empfohlen)", "CSV"],
                        index=0
                    )

                    # Datei exportieren
                    if export_format == "Excel (empfohlen)":
                        @st.cache_data
                        def convert_to_excel(df):
                            output = BytesIO()
                            df.to_excel(output, index=False, engine='openpyxl')
                            output.seek(0)
                            return output

                        output_file = convert_to_excel(average_sales)
                        st.download_button("Ergebnisse herunterladen", data=output_file, file_name="ergebnisse.xlsx")
                    elif export_format == "CSV":
                        @st.cache_data
                        def convert_to_csv(df):
                            return df.to_csv(index=False).encode('utf-8')

                        output_file = convert_to_csv(average_sales)
                        st.download_button("Ergebnisse herunterladen", data=output_file, file_name="ergebnisse.csv")
            except Exception as e:
                st.error(f"Fehler bei der Verarbeitung der Datei: {e}")

    # Credits und Datenschutz
    st.markdown("---")
    st.markdown("⚠️ **Hinweis:** Diese Anwendung speichert keine Daten und hat keinen Zugriff auf Ihre Dateien.")
    st.markdown("🌟 **Erstellt von Christoph R. Kaiser mit Hilfe von Künstlicher Intelligenz.**")

elif st.session_state.navigation == "Anleitung":
    # Anleitung anzeigen
    st.markdown("""
    ### Anleitung zur Nutzung dieser App
    1. Bereiten Sie Ihre Abverkaufsdaten vor:
       - Die Datei muss die Spalten **'Artikel', 'Woche', 'Menge' (in Stück) und 'Name'** enthalten.
       - Speichern Sie die Datei im Excel- oder CSV-Format.
    2. Laden Sie Ihre Datei hoch:
       - Nutzen Sie die Schaltfläche **„Durchsuchen“**, um Ihre Datei auszuwählen.
    3. Überprüfen Sie die berechneten Ergebnisse:
       - Die App zeigt die durchschnittlichen Abverkaufsmengen pro Woche an.
    4. Wählen Sie das gewünschte Exportformat:
       - Standardmäßig wird Excel empfohlen.
    5. Laden Sie die Ergebnisse herunter:
       - Nutzen Sie die Schaltfläche **„Ergebnisse herunterladen“**, um die berechneten Daten zu speichern.
    """)

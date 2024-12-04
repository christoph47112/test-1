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
navigation = st.sidebar.radio("Navigation", ["Modul", "Anleitung"])
st.sidebar.download_button(
    label="Beispieldatei herunterladen",
    data=example_file,
    file_name="beispiel_abverkauf.xlsx"
)

# Funktion zur Verarbeitung der Verkaufsdaten
def process_sales_data(dataframe):
    # Berechne den durchschnittlichen Abverkauf pro Artikel
    average_sales = dataframe.groupby('Artikel')['Menge'].mean().reset_index()
    average_sales.rename(columns={'Menge': 'Durchschnittliche Menge pro Woche'}, inplace=True)
    
    # Behalte die ursprüngliche Reihenfolge der Artikel bei
    sorted_sales = dataframe[['Artikel', 'Name']].drop_duplicates().merge(
        average_sales, on='Artikel', how='left'
    )
    return sorted_sales

# Modul anzeigen
if navigation == "Modul":
    # Datei-Uploader
    uploaded_file = st.file_uploader("Bitte laden Sie Ihre Datei hoch (Excel)", type=["xlsx"])

    if uploaded_file:
        # Excel-Datei laden und verarbeiten
        data = pd.ExcelFile(uploaded_file)
        sheet_name = data.sheet_names[0]  # Nimmt an, dass das erste Blatt relevant ist
        df = data.parse(sheet_name)

        # Daten verarbeiten
        result = process_sales_data(df)

        # Ergebnisse anzeigen
        st.subheader("Ergebnisse")
        st.dataframe(result)

        # Ergebnisse herunterladen
        output = BytesIO()
        result.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)
        st.download_button(
            label="Ergebnisse herunterladen",
            data=output,
            file_name="durchschnittliche_abverkaeufe.xlsx"
        )

    # Credits und Datenschutz
    st.markdown("---")
    st.markdown("⚠️ **Hinweis:** Diese Anwendung speichert keine Daten und hat keinen Zugriff auf Ihre Dateien.")
    st.markdown("🌟 **Erstellt von Christoph R. Kaiser mit Hilfe von Künstlicher Intelligenz.**")

# Anleitung anzeigen
elif navigation == "Anleitung":
    # Anleitung anzeigen
    st.markdown("""
    ### Anleitung zur Nutzung dieser App
    1. Bereiten Sie Ihre Abverkaufsdaten vor:
       - Die Datei muss die Spalten **'Artikel', 'Woche', 'Menge' (in Stück) und 'Name'** enthalten.
       - Speichern Sie die Datei im Excel-Format.
    2. Laden Sie Ihre Datei hoch:
       - Nutzen Sie die Schaltfläche **„Durchsuchen“**, um Ihre Datei auszuwählen.
    3. Überprüfen Sie die berechneten Ergebnisse:
       - Die App zeigt die durchschnittlichen Abverkaufsmengen pro Woche an.
    4. Laden Sie die Ergebnisse herunter:
       - Nutzen Sie die Schaltfläche **„Ergebnisse herunterladen“**, um die berechneten Daten zu speichern.

    ---
    ⚠️ **Hinweis:** Diese Anwendung speichert keine Daten und hat keinen Zugriff auf Ihre Dateien.
    
    🌟 **Erstellt von Christoph R. Kaiser mit Hilfe von Künstlicher Intelligenz.**
    """)

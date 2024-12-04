import pandas as pd
import streamlit as st
from io import BytesIO

# Title and Page Layout
st.set_page_config(page_title="Abverkaufsmengen Berechnung", layout="wide")
st.title("Berechnung der ∅ Abverkaufsmengen pro Woche von Werbeartikeln zu Normalpreisen")

# Initialize session state for toggle functionality
if "show_module" not in st.session_state:
    st.session_state["show_module"] = False

# Display Anleitung
st.markdown("""
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
""")

# Add the button below the Anleitung
button_label = (
    "Nur Anleitung anzeigen" if st.session_state["show_module"] else "Modul benutzen und Anleitung anzeigen"
)
if st.button(button_label):
    st.session_state["show_module"] = not st.session_state["show_module"]

# Display example file download option below the button
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
    label="Beispieldatei herunterladen",
    data=example_file,
    file_name="beispiel_abverkauf.xlsx"
)

# Display the module if the toggle is enabled
if st.session_state["show_module"]:
    st.subheader("Modul")
    # File Uploader
    uploaded_file = st.file_uploader("Bitte laden Sie Ihre Datei hoch (Excel oder CSV)", type=["xlsx", "csv"])

    if uploaded_file:
        with st.spinner("Die Datei wird verarbeitet..."):
            try:
                # File Handling
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.ExcelFile(uploaded_file).parse(0)

                # Validate required columns
                required_columns = {"Artikel", "Woche", "Menge", "Name"}
                if not required_columns.issubset(df.columns):
                    st.error("Fehler: Die Datei muss die Spalten 'Artikel', 'Woche', 'Menge' und 'Name' enthalten.")
                else:
                    # Calculate average sales
                    average_sales = df.groupby('Artikel')['Menge'].mean().reset_index()
                    average_sales.rename(columns={'Menge': 'Durchschnittliche Menge pro Woche'}, inplace=True)

                    # Merge with original data for sorting
                    sorted_sales = df[['Artikel', 'Name']].drop_duplicates().merge(
                        average_sales, on='Artikel', how='left'
                    )

                    # Display Results
                    st.subheader("Ergebnisse")
                    st.dataframe(sorted_sales)

                    # Export Format Selection
                    st.subheader("Wählen Sie das Exportformat:")
                    export_format = st.radio(
                        "Exportformat auswählen:",
                        ["Excel (empfohlen)", "CSV"],
                        index=0
                    )

                    # Export Results
                    if export_format == "Excel (empfohlen)":
                        @st.cache_data
                        def convert_to_excel(df):
                            output = BytesIO()
                            df.to_excel(output, index=False, engine='openpyxl')
                            output.seek(0)
                            return output

                        output_file = convert_to_excel(sorted_sales)
                        st.download_button("Ergebnisse herunterladen", data=output_file, file_name="ergebnisse.xlsx")
                    elif export_format == "CSV":
                        @st.cache_data
                        def convert_to_csv(df):
                            return df.to_csv(index=False).encode('utf-8')

                        output_file = convert_to_csv(sorted_sales)
                        st.download_button("Ergebnisse herunterladen", data=output_file, file_name="ergebnisse.csv")
            except Exception as e:
                st.error(f"Fehler bei der Verarbeitung der Datei: {e}")

    # Disclaimer and Credits
    st.markdown("---")
    st.markdown("⚠️ **Hinweis:** Diese Anwendung speichert keine Daten und hat keinen Zugriff auf Ihre Dateien.")
    st.markdown("🌟 **Erstellt von Christoph R. Kaiser mit Hilfe von Künstlicher Intelligenz.**")

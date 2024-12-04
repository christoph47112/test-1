import pandas as pd
import streamlit as st
from io import BytesIO

# Title and Page Layout
st.set_page_config(page_title="Durchschnittliche Abverkäufe Berechnung", layout="wide")
st.title("Durchschnittliche Abverkäufe Berechnung")
st.write("Laden Sie eine Excel-Datei hoch, um die durchschnittlichen Verkäufe pro Woche zu berechnen.")

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

# Datei-Uploader
uploaded_file = st.file_uploader("Excel-Datei hochladen", type=["xlsx"])
if uploaded_file:
    # Excel-Datei laden und verarbeiten
    data = pd.ExcelFile(uploaded_file)
    sheet_name = data.sheet_names[0]  # Nimmt an, dass das erste Blatt relevant ist
    df = data.parse(sheet_name)

    # Daten verarbeiten
    result = process_sales_data(df)

    # Ergebnisse anzeigen
    st.write("Ergebnisse:")
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

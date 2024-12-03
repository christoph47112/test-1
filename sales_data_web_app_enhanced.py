
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Multilingual support
language = st.sidebar.selectbox("Sprache / Language", ["Deutsch", "English"])

# Texts in different languages
texts = {
    "Deutsch": {
        "title": "Berechnung der ∅ Abverkaufsmengen pro Woche von Werbeartikeln zu Normalpreisen",
        "upload_prompt": "Bitte laden Sie Ihre Excel-Datei hoch",
        "processing_message": "Die Datei wird verarbeitet...",
        "error_message": "Fehler: Die Datei muss die Spalten 'Artikel', 'Menge' und 'Name' enthalten.",
        "results": "Ergebnisse",
        "download": "Laden Sie die Ergebnisse herunter",
        "example": "Laden Sie eine Beispieldatei herunter"
    },
    "English": {
        "title": "Calculation of ∅ Weekly Sales Volumes for Promotional Items at Regular Prices",
        "upload_prompt": "Please upload your Excel file",
        "processing_message": "Processing your file...",
        "error_message": "Error: The file must contain the columns 'Artikel', 'Menge', and 'Name'.",
        "results": "Results",
        "download": "Download Results",
        "example": "Download an Example File"
    }
}
text = texts[language]

# Example file download
example_data = {
    "Artikel": ["001", "002", "003"],
    "Name": ["Item A", "Item B", "Item C"],
    "Menge": [100, 150, 200]
}
example_df = pd.DataFrame(example_data)
st.sidebar.download_button(label=text["example"], data=example_df.to_csv(index=False), file_name="example.csv")

# Title
st.title(text["title"])

# File uploader
uploaded_file = st.file_uploader(text["upload_prompt"], type=["xlsx", "csv"])

if uploaded_file:
    st.info(text["processing_message"])
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.ExcelFile(uploaded_file).parse(0)
        
        # Validate required columns
        required_columns = {"Artikel", "Name", "Menge"}
        if not required_columns.issubset(df.columns):
            st.error(text["error_message"])
        else:
            # Calculate average sales
            average_sales = df.groupby('Artikel')['Menge'].mean().reset_index()
            average_sales.rename(columns={'Menge': 'Durchschnittliche Menge pro Woche'}, inplace=True)
            
            # Merge with original data for sorting
            sorted_sales = df[['Artikel', 'Name']].drop_duplicates().merge(
                average_sales, on='Artikel', how='left'
            )
            
            # Display results
            st.subheader(text["results"])
            st.dataframe(sorted_sales)
            
            # Visualization
            st.subheader("Visuelle Darstellung (Visual Representation)")
            fig, ax = plt.subplots()
            sorted_sales.plot(kind='bar', x='Name', y='Durchschnittliche Menge pro Woche', ax=ax, legend=False)
            ax.set_ylabel('Durchschnittliche Menge (Average Amount)')
            st.pyplot(fig)
            
            # Download results
            output_file = "durchschnittliche_abverkaufsdaten.xlsx"
            sorted_sales.to_excel(output_file, index=False)
            with open(output_file, "rb") as file:
                st.download_button(text["download"], file, file_name=output_file)
    
    except Exception as e:
        st.error(f"Error processing file: {e}")

st.markdown("---")
st.markdown(
    "⚠️ **Hinweis:** Diese Anwendung speichert keine Daten und hat keinen Zugriff auf Ihre Dateien. "
    "Alle Verarbeitungen erfolgen lokal auf Ihrem Gerät oder auf dem temporären Streamlit-Server."
)
st.markdown(
    "🌟 **Erstellt von Christoph R. Kaiser mit Hilfe von Künstlicher Intelligenz.**"
)

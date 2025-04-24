import streamlit as st
import pandas as pd
import zipfile
import io
import difflib
import os
import tempfile

def main():
    st.set_page_config(page_title="Porovnání žákovských prací", layout="wide")
    
    st.title("Nástroj pro porovnávání žákovských prací se vzorovým textem")
    
    # Vytvoření záložek
    tab1, tab2 = st.tabs(["Nahrání a porovnání", "Nápověda"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Vzorový text")
            vzorovy_text_upload = st.file_uploader("Nahrajte vzorový text", type=["txt"])
            vzorovy_text = ""
            
            if vzorovy_text_upload is not None:
                vzorovy_text = vzorovy_text_upload.getvalue().decode("utf-8")
                st.text_area("Obsah vzorového textu", vzorovy_text, height=300)
        
        with col2:
            st.subheader("Žákovské práce")
            st.write("Nahrajte ZIP soubor obsahující žákovské práce ve formátu .txt")
            zakovske_prace_upload = st.file_uploader("Nahrajte ZIP soubor s pracemi", type=["zip"])
            
            if zakovske_prace_upload is not None:
                st.success(f"Úspěšně nahrán soubor: {zakovske_prace_upload.name}")
        
        if vzorovy_text_upload is not None and zakovske_prace_upload is not None:
            if st.button("Porovnat práce"):
                with st.spinner("Probíhá porovnávání..."):
                    vysledky = porovnej_prace(vzorovy_text, zakovske_prace_upload)
                    zobraz_vysledky(vysledky)
    
    with tab2:
        zobraz_napovedu()

def porovnej_prace(vzorovy_text, zakovske_prace_zip):
    """Porovná vzorový text s žákovskými pracemi v ZIP souboru."""
    vysledky = []
    
    # Vytvoření dočasného adresáře pro rozbalení ZIP souboru
    with tempfile.TemporaryDirectory() as tmpdirname:
        with zipfile.ZipFile(zakovske_prace_zip, 'r') as zip_ref:
            zip_ref.extractall(tmpdirname)
        
        # Procházení všech souborů v dočasném adresáři
        for filename in os.listdir(tmpdirname):
            if filename.endswith('.txt'):
                file_path = os.path.join(tmpdirname, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    try:
                        zakovska_prace = file.read()
                        
                        # Výpočet podobnosti pomocí difflib
                        similar = difflib.SequenceMatcher(None, vzorovy_text, zakovska_prace).ratio()
                        podobnost_procenta = similar * 100
                        
                        # Porovnání a získání rozdílů
                        vzor_lines = vzorovy_text.splitlines()
                        zak_lines = zakovska_prace.splitlines()
                        diff = list(difflib.unified_diff(vzor_lines, zak_lines, lineterm=''))
                        
                        # Odstranění metadat diff výstupu (prvních pár řádků)
                        diff = diff[3:] if len(diff) > 3 else []
                        
                        # Přidání výsledku do seznamu
                        vysledky.append({
                            "jmeno_souboru": filename,
                            "podobnost": podobnost_procenta,
                            "diff": '\n'.join(diff),
                            "text_zaka": zakovska_prace
                        })
                    except Exception as e:
                        st.error(f"Chyba při zpracování souboru {filename}: {str(e)}")
    
    # Seřazení výsledků podle podobnosti
    vysledky.sort(key=lambda x: x["podobnost"], reverse=True)
    return vysledky

def zobraz_vysledky(vysledky):
    """Zobrazí výsledky porovnání."""
    st.header("Výsledky porovnání")
    
    # Vytvoření DataFrame pro přehlednou tabulku
    df = pd.DataFrame([{
        "Soubor": v["jmeno_souboru"],
        "Podobnost (%)": round(v["podobnost"], 2)
    } for v in vysledky])
    
    st.dataframe(df)
    
    # Zobrazení detailů každé práce
    st.header("Detaily jednotlivých prací")
    for i, vysledek in enumerate(vysledky):
        with st.expander(f"{vysledek['jmeno_souboru']} - Podobnost: {round(vysledek['podobnost'], 2)}%"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Text žáka")
                st.text_area("", vysledek["text_zaka"], height=200, key=f"text_{i}")
            
            with col2:
                st.subheader("Rozdíly")
                st.text_area("", vysledek["diff"], height=200, key=f"diff_{i}")
                st.write("Legenda:")
                st.write("- Řádky začínající `-` jsou ve vzorovém textu, ale chybí v práci žáka")
                st.write("- Řádky začínající `+` jsou v práci žáka, ale nejsou ve vzorovém textu")

def zobraz_napovedu():
    """Zobrazí nápovědu pro použití aplikace."""
    st.header("Jak používat tento nástroj")
    
    st.write("""
    ### 1. Příprava souborů
    - **Vzorový text:** Připravte jeden soubor .txt s vzorovým textem.
    - **Žákovské práce:** Připravte soubory .txt pro každou žákovskou práci a zabalte je do ZIP souboru.
    
    ### 2. Nahrání souborů
    - Nahrajte vzorový text pomocí prvního uploaderu.
    - Nahrajte ZIP soubor s žákovskými pracemi pomocí druhého uploaderu.
    
    ### 3. Porovnání
    - Klikněte na tlačítko "Porovnat práce".
    - Aplikace porovná všechny žákovské práce se vzorovým textem a zobrazí výsledky.
    
    ### 4. Interpretace výsledků
    - **Tabulka podobnosti:** Zobrazuje procentuální podobnost každé práce se vzorovým textem.
    - **Detaily:** Kliknutím na řádek v tabulce zobrazíte detailní porovnání včetně rozdílů.
    - **Rozdíly:** 
        - Řádky začínající `-` jsou ve vzorovém textu, ale chybí v práci žáka.
        - Řádky začínající `+` jsou v práci žáka, ale nejsou ve vzorovém textu.
    """)
    
    st.info("Poznámka: Tento nástroj je určen pouze pro textové soubory (.txt) v kódování UTF-8.")

if __name__ == "__main__":
    main()

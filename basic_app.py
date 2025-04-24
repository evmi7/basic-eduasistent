def porovnej_prace_ai(vzorovy_text, zakovske_prace_zip):
    """Porovná vzorový text s žákovskými pracemi v ZIP souboru pomocí AI."""
    vysledky = []
    
    # Vytvoření dočasného adresáře pro rozbalení ZIP souboru
    with tempfile.TemporaryDirectory() as tmpdirname:
        with zipfile.ZipFile(zakovske_prace_zip, 'r') as zip_ref:
            zip_ref.extractall(tmpdirname)
        
        # Procházení všech souborů v dočasném adresáři
        for filename in os.listdir(tmpdirname):
            if filename.endswith('.txt'):
                file_path = os.path.join(tmpdirname, filename)
                
                # Zkusíme nejprve Windows-1250 a poté další kódování
                encodings = ['windows-1250', 'cp1250', 'iso-8859-2', 'utf-8']
                zakovska_prace = None
                
                for encoding in encodings:
                    try:
                        with open(file_path, 'r', encoding=encoding) as file:
                            zakovska_prace = file.read()
                            break
                    except UnicodeDecodeError:
                        continue
                
                if zakovska_prace is None:
                    st.warning(f"Nepodařilo se přečíst soubor {filename} s žádným známým kódováním.")
                    continue
                
                try:
                    # Výpočet podobnosti pomocí difflib pro základní metriku
                    similar = difflib.SequenceMatcher(None, vzorovy_text, zakovska_prace).ratio()
                    podobnost_procenta = similar * 100
                    
                    # Získání AI analýzy
                    ai_analyza = analyze_text(vzorovy_text, zakovska_prace)
                    
                    # Přidání výsledku do seznamu
                    vysledky.append({
                        "jmeno_souboru": filename,
                        "podobnost": podobnost_procenta,
                        "text_zaka": zakovska_prace,
                        "ai_analyza": ai_analyza
                    })
                except Exception as e:
                    st.error(f"Chyba při zpracování souboru {filename}: {str(e)}")
    
    # Seřazení výsledků podle podobnosti
    vysledky.sort(key=lambda x: x["podobnost"], reverse=True)
    return vysledky

def zobraz_vysledky_ai(vysledky):
    """Zobrazí výsledky AI analýzy."""
    st.header("Výsledky AI analýzy")
    
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
                st.text_area("", vysledek["text_zaka"], height=200, key=f"text_ai_{i}")
            
            with col2:
                st.subheader("AI analýza")
                st.markdown(vysledek["ai_analyza"], unsafe_allow_html=False)import streamlit as st
import pandas as pd
import zipfile
import io
import difflib
import os
import tempfile
from openai import OpenAI

def get_openai_client():
    """Vytvoří a vrátí klienta OpenAI API."""
    api_key = st.session_state.get('openai_api_key', '')
    if not api_key:
        return None
    return OpenAI(api_key=api_key)

def analyze_text(reference_text, student_text):
    """Použije OpenAI API pro porovnání a analýzu textů."""
    client = get_openai_client()
    if not client:
        return "Pro AI analýzu je nutné zadat API klíč OpenAI."
    
    prompt = f"""
Porovnej následující text žáka s ideálním vzorovým textem. Uveď:

1. Hlavní rozdíly, chyby nebo nedostatky.
2. Doporučení k vylepšení.
3. Odhadni celkové hodnocení na stupnici 1 (nejhorší) až 5 (výborné).

--- VZOR ---
{reference_text}

--- ŽÁK ---
{student_text}

Odpověď formuluj česky, přehledně.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Chyba při komunikaci s OpenAI API: {e}"

def main():
    st.set_page_config(page_title="Porovnání žákovských prací", layout="wide")
    
    # Inicializace session state pro API klíč
    if 'openai_api_key' not in st.session_state:
        st.session_state.openai_api_key = ""
    
    st.title("Nástroj pro porovnávání žákovských prací se vzorovým textem")
    
    # Vytvoření záložek
    tab1, tab2, tab3 = st.tabs(["Nahrání a porovnání", "Nastavení", "Nápověda"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Vzorový text")
            vzorovy_text_upload = st.file_uploader("Nahrajte vzorový text", type=["txt"])
            vzorovy_text = ""
            
            if vzorovy_text_upload is not None:
                # Zkusíme nejprve Windows-1250 (preferované ve škole) a poté další kódování
                encodings = ['windows-1250', 'cp1250', 'iso-8859-2', 'utf-8']
                vzorovy_text = None
                
                for encoding in encodings:
                    try:
                        vzorovy_text = vzorovy_text_upload.getvalue().decode(encoding)
                        st.success(f"Soubor úspěšně přečten s kódováním {encoding}")
                        break
                    except UnicodeDecodeError:
                        continue
                
                if vzorovy_text is None:
                    st.error("Nepodařilo se přečíst soubor. Zkuste jej uložit v kódování Windows-1250.")
                    vzorovy_text = ""
                else:
                    st.text_area("Obsah vzorového textu", vzorovy_text, height=300)
        
        with col2:
            st.subheader("Žákovské práce")
            st.write("Nahrajte ZIP soubor obsahující žákovské práce ve formátu .txt")
            zakovske_prace_upload = st.file_uploader("Nahrajte ZIP soubor s pracemi", type=["zip"])
            
            if zakovske_prace_upload is not None:
                st.success(f"Úspěšně nahrán soubor: {zakovske_prace_upload.name}")
        
        # Volba typu analýzy
        typ_analyzy = st.radio(
            "Vyberte typ analýzy:",
            ["Základní porovnání", "AI analýza (vyžaduje OpenAI API klíč)"]
        )
        
        if vzorovy_text_upload is not None and zakovske_prace_upload is not None:
            if st.button("Porovnat práce"):
                with st.spinner("Probíhá porovnávání..."):
                    if typ_analyzy == "Základní porovnání":
                        vysledky = porovnej_prace(vzorovy_text, zakovske_prace_upload)
                        zobraz_vysledky(vysledky)
                    else:
                        if not st.session_state.openai_api_key:
                            st.error("Pro použití AI analýzy zadejte nejprve API klíč OpenAI v záložce Nastavení.")
                        else:
                            vysledky = porovnej_prace_ai(vzorovy_text, zakovske_prace_upload)
                            zobraz_vysledky_ai(vysledky)
    
    with tab2:
        st.subheader("Nastavení API klíče")
        api_key = st.text_input("OpenAI API klíč (pro AI analýzu)", 
                             value=st.session_state.openai_api_key,
                             type="password")
        if st.button("Uložit API klíč"):
            st.session_state.openai_api_key = api_key
            st.success("API klíč byl uložen.")
    
    with tab3:
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
                
                # Zkusíme nejprve Windows-1250 a poté další kódování
                encodings = ['windows-1250', 'cp1250', 'iso-8859-2', 'utf-8']
                zakovska_prace = None
                
                for encoding in encodings:
                    try:
                        with open(file_path, 'r', encoding=encoding) as file:
                            zakovska_prace = file.read()
                            break
                    except UnicodeDecodeError:
                        continue
                
                if zakovska_prace is None:
                    st.warning(f"Nepodařilo se přečíst soubor {filename} s žádným známým kódováním.")
                    continue
                
                try:
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
    - **Vzorový text:** Připravte jeden soubor .txt s vzorovým textem (ideálně v kódování Windows-1250).
    - **Žákovské práce:** Připravte soubory .txt pro každou žákovskou práci a zabalte je do ZIP souboru.
    
    ### 2. Nahrání souborů
    - Nahrajte vzorový text pomocí prvního uploaderu.
    - Nahrajte ZIP soubor s žákovskými pracemi pomocí druhého uploaderu.
    
    ### 3. Volba typu analýzy
    - **Základní porovnání:** Rychlé porovnání založené na rozdílech v textu.
    - **AI analýza:** Podrobnější analýza s využitím OpenAI API (vyžaduje API klíč).
    
    ### 4. Porovnání
    - Klikněte na tlačítko "Porovnat práce".
    - Aplikace porovná všechny žákovské práce se vzorovým textem a zobrazí výsledky.
    
    ### 5. Interpretace výsledků
    - **Tabulka podobnosti:** Zobrazuje procentuální podobnost každé práce se vzorovým textem.
    - **Základní porovnání:**
        - Zobrazí rozdíly v textu (řádky začínající `-` jsou ve vzorovém textu, řádky začínající `+` jsou v práci žáka).
    - **AI analýza:**
        - Poskytne strukturovanou zpětnou vazbu zahrnující hlavní rozdíly, doporučení k vylepšení a celkové hodnocení.
    """)
    
    st.info("Poznámka: Aplikace je optimalizována pro soubory v kódování Windows-1250, které je standardem na vaší škole, ale podporuje i další kódování.")
    
    st.warning("Pro použití AI analýzy je nutné zadat platný OpenAI API klíč v záložce Nastavení.")


if __name__ == "__main__":
    main()

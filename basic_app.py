import streamlit as st

# DŮLEŽITÉ: set_page_config musí být první Streamlit příkaz v aplikaci
st.set_page_config(
    page_title="Analytický nástroj pro práce žáků",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

import re
from collections import Counter
import math

# Funkce pro předzpracování textu
def preprocess_text(text):
    if not isinstance(text, str):
        return ""
    # Převod na malá písmena
    text = text.lower()
    # Odstranění interpunkce a čísel
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)
    # Odstranění extra mezer
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Funkce pro výpočet podobnosti textů (vlastní implementace kosinové podobnosti)
def calculate_similarity(text1, text2):
    # Předzpracování textů
    processed_text1 = preprocess_text(text1)
    processed_text2 = preprocess_text(text2)
    
    # Rozdělení na slova
    words1 = processed_text1.split()
    words2 = processed_text2.split()
    
    # Vytvoření vektorů četnosti slov
    word_set = set(words1 + words2)
    
    # Počítání frekvence slov
    vec1 = {word: words1.count(word) for word in word_set}
    vec2 = {word: words2.count(word) for word in word_set}
    
    # Výpočet kosinové podobnosti
    dot_product = sum(vec1.get(word, 0) * vec2.get(word, 0) for word in word_set)
    
    # Velikost vektorů
    magnitude1 = math.sqrt(sum(value ** 2 for value in vec1.values()))
    magnitude2 = math.sqrt(sum(value ** 2 for value in vec2.values()))
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0
    
    return dot_product / (magnitude1 * magnitude2)

# Funkce pro získání klíčových slov
def get_keywords(text, top_n=10):
    # Předzpracování textu
    processed_text = preprocess_text(text)
    
    # Rozdělení na slova
    words = processed_text.split()
    
    # Jednoduchý seznam stop slov pro češtinu
    stop_words = {'a', 'aby', 'ale', 'ani', 'až', 'být', 'co', 'či', 'do', 'i', 'jak', 'je', 'jeho', 'její', 'jejich',
                 'jen', 'jenž', 'ji', 'jich', 'již', 'jsem', 'jsou', 'k', 'kde', 'když', 'me', 'mezi', 'mi', 'mít',
                 'mně', 'mnou', 'my', 'na', 'nad', 'nebo', 'neboť', 'než', 'ní', 'o', 'od', 'on', 'ona', 'oni', 'ono',
                 'po', 'pod', 'podle', 'pokud', 'pro', 'proto', 'protože', 'před', 'při', 's', 'se', 'si', 'svůj',
                 'ta', 'tak', 'také', 'takže', 'tam', 'tedy', 'ten', 'tento', 'to', 'tohle', 'toto', 'ty', 'u', 'už',
                 'v', 've', 'však', 'všechen', 'vy', 'z', 'za', 'ze', 'že'}
    
    # Filtrace stop slov
    filtered_words = [word for word in words if word not in stop_words and len(word) > 1]
    
    # Počítání frekvence slov
    word_counts = Counter(filtered_words)
    
    # Vrácení top N slov
    return word_counts.most_common(top_n)

# Funkce pro porovnání klíčových slov
def compare_keywords(text1, text2, top_n=10):
    # Získání klíčových slov z obou textů
    keywords1 = get_keywords(text1, top_n)
    keywords2 = get_keywords(text2, top_n)
    
    # Převod na slovníky pro jednodušší manipulaci
    keywords1_dict = dict(keywords1)
    keywords2_dict = dict(keywords2)
    
    # Získání množin slov
    words1_set = set(keywords1_dict.keys())
    words2_set = set(keywords2_dict.keys())
    
    # Nalezení společných a unikátních slov
    common_words = words1_set.intersection(words2_set)
    missing_words = words1_set - words2_set
    extra_words = words2_set - words1_set
    
    return keywords1, keywords2, common_words, missing_words, extra_words

# Funkce pro analýzu délky textu
def analyze_length(text1, text2):
    if not isinstance(text1, str) or not isinstance(text2, str):
        return {"text1": 0, "text2": 0, "diff_percent": 0}
    
    # Počet slov
    words1 = len(re.findall(r'\b\w+\b', text1))
    words2 = len(re.findall(r'\b\w+\b', text2))
    
    # Rozdíl v procentech
    if words1 > 0:
        diff_percent = ((words2 - words1) / words1) * 100
    else:
        diff_percent = 0
    
    return {
        "text1": words1,
        "text2": words2,
        "diff_percent": diff_percent
    }

# Hlavní nadpis aplikace
st.title("🔍 Analytický nástroj pro porovnávání žákovských prací")
st.write("Tento nástroj umožňuje porovnat práci žáka se vzorovým řešením a analyzovat podobnosti a rozdíly.")

# Vytvoření záložek pro různé typy analýz
tab1, tab2 = st.tabs(["Textová analýza", "Nastavení"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("Vzorové řešení")
        reference_text = st.text_area("Vložte vzorový text", height=250)
    
    with col2:
        st.header("Práce žáka")
        student_text = st.text_area("Vložte text žáka", height=250)
    
    # Tlačítko pro provedení analýzy
    if st.button("Provést analýzu"):
        if reference_text and student_text:
            st.divider()
            st.header("Výsledky analýzy")
            
            # Výpočet podobnosti
            similarity = calculate_similarity(reference_text, student_text)
            st.metric("Míra podobnosti", f"{similarity*100:.2f}%")
            
            # Analýza délky textu
            length_analysis = analyze_length(reference_text, student_text)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Počet slov ve vzoru", length_analysis["text1"])
            with col2:
                st.metric("Počet slov v práci žáka", length_analysis["text2"])
            with col3:
                diff_label = "Rozdíl délky"
                diff_value = f"{length_analysis['diff_percent']:.2f}%"
                diff_delta = f"{'+' if length_analysis['diff_percent'] > 0 else ''}{length_analysis['diff_percent']:.2f}%"
                st.metric(diff_label, diff_value, diff_delta)
            
            # Porovnání klíčových slov
            st.subheader("Porovnání klíčových slov")
            keywords1, keywords2, common_words, missing_words, extra_words = compare_keywords(reference_text, student_text)
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Nejčastější slova ve vzoru:**")
                for word, count in keywords1:
                    st.write(f"- {word}: {count}x")
            
            with col2:
                st.write("**Nejčastější slova v práci žáka:**")
                for word, count in keywords2:
                    st.write(f"- {word}: {count}x")
            
            # Společná a chybějící slova
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Společná klíčová slova:**")
                for word in common_words:
                    st.write(f"- {word}")
            
            with col2:
                st.write("**Chybějící klíčová slova:**")
                for word in missing_words:
                    st.write(f"- {word}")
            
            st.write("**Nadbytečná klíčová slova v práci žáka:**")
            for word in extra_words:
                st.write(f"- {word}")
        else:
            st.warning("Pro provedení analýzy je třeba vyplnit oba texty.")

with tab2:
    st.header("Nastavení analýzy")
    st.write("Zde můžete upravit parametry analýzy.")
    
    # Nastavení analýzy
    st.subheader("Parametry textové analýzy")
    keyword_count = st.slider(
        "Počet klíčových slov pro porovnání",
        min_value=5,
        max_value=30,
        value=10,
        step=1
    )
    
    st.info("Tato nastavení budou použita při další analýze. Změny se projeví po stisknutí tlačítka 'Provést analýzu'.")

# Postranní panel s nápovědou
with st.sidebar:
    st.header("Nápověda")
    st.write("""
    **Jak používat tento nástroj:**
    
    1. Vložte vzorové řešení do levého textového pole
    2. Vložte práci žáka do pravého textového pole
    3. Klikněte na tlačítko 'Provést analýzu'
    4. Prozkoumejte výsledky analýzy
    
    **Co výsledky znamenají:**
    
    - **Míra podobnosti**: Hodnota mezi 0-100%, kde vyšší hodnota znamená větší podobnost textů
    - **Počet slov**: Porovnání délky textů
    - **Klíčová slova**: Nejčastější důležitá slova v obou textech
    - **Společná slova**: Klíčová slova obsažená v obou textech
    - **Chybějící slova**: Klíčová slova ze vzoru, která chybí v práci žáka
    """)
    
    st.divider()
    st.write("© 2025 Analytický nástroj pro porovnávání prací")

import streamlit as st

# DŮLEŽITÉ: set_page_config musí být první Streamlit příkaz v aplikaci
st.set_page_config(
    page_title="Analytický nástroj pro práce žáků",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Stáhnout potřebné balíčky NLTK při prvním spuštění
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

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

# Funkce pro výpočet podobnosti textů
def calculate_similarity(text1, text2, method='cosine'):
    # Předzpracování textů
    processed_text1 = preprocess_text(text1)
    processed_text2 = preprocess_text(text2)
    
    # Výběr metody pro vektorizaci
    if method == 'tfidf':
        vectorizer = TfidfVectorizer()
    else:  # výchozí metoda je 'cosine'
        vectorizer = CountVectorizer()
    
    # Vektorizace textů
    try:
        vectors = vectorizer.fit_transform([processed_text1, processed_text2])
        # Výpočet podobnosti
        similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        return similarity
    except Exception as e:
        st.error(f"Chyba při výpočtu podobnosti: {e}")
        return 0

# Funkce pro porovnání klíčových slov
def compare_keywords(text1, text2, top_n=10):
    # Předzpracování textů
    processed_text1 = preprocess_text(text1)
    processed_text2 = preprocess_text(text2)
    
    # Získání stop slov (nerelevantních slov)
    try:
        stop_words = set(stopwords.words('czech'))
    except:
        stop_words = set()  # Pokud není dostupná čeština, použijeme prázdnou množinu
    
    # Tokenizace a odstranění stop slov
    words1 = [word for word in word_tokenize(processed_text1) if word not in stop_words and len(word) > 1]
    words2 = [word for word in word_tokenize(processed_text2) if word not in stop_words and len(word) > 1]
    
    # Počítání frekvence slov
    word_freq1 = pd.Series(words1).value_counts().head(top_n)
    word_freq2 = pd.Series(words2).value_counts().head(top_n)
    
    return word_freq1, word_freq2

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
            keywords1, keywords2 = compare_keywords(reference_text, student_text)
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Nejčastější slova ve vzoru:**")
                for word, count in keywords1.items():
                    st.write(f"- {word}: {count}x")
            
            with col2:
                st.write("**Nejčastější slova v práci žáka:**")
                for word, count in keywords2.items():
                    st.write(f"- {word}: {count}x")
            
            # Společná a chybějící slova
            common_words = set(keywords1.index).intersection(set(keywords2.index))
            missing_words = set(keywords1.index).difference(set(keywords2.index))
            extra_words = set(keywords2.index).difference(set(keywords1.index))
            
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
    similarity_method = st.selectbox(
        "Metoda výpočtu podobnosti",
        options=["cosine", "tfidf"],
        index=0,
        help="Kosinová podobnost je standardní metoda. TF-IDF dává větší váhu méně častým slovům."
    )
    
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

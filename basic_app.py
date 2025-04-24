import streamlit as st

# Nastavení stránky
st.set_page_config(
    page_title="EDUasistent - Základní verze",
    page_icon="📝",
    layout="wide"
)

# Nadpis a úvod
st.title("📝 EDUasistent - Hodnocení textů")
st.markdown("""
    Aplikace pro automatické porovnání a hodnocení textů žáků vůči vzorovému textu pomocí AI.
    
    Toto je základní verze aplikace bez funkcionality Pandas a OpenAI.
""")

# Sidebar pro nastavení
with st.sidebar:
    st.header("Nastavení")
    st.info("Základní verze aplikace bez pokročilých funkcí.")

# Hlavní část aplikace
col1, col2 = st.columns(2)

with col1:
    st.header("Nahrání souborů")
    st.subheader("1. Nahrajte vzorový text")
    reference_file = st.file_uploader("Vzorový text (*.txt)", type="txt", key="reference")
    
    st.subheader("2. Nahrajte texty žáků")
    student_files = st.file_uploader("Práce žáků (*.txt)", type="txt", accept_multiple_files=True, key="students")
    
    st.subheader("3. Spusťte analýzu")
    analyze_button = st.button("🔍 Analyzovat texty", type="primary", disabled=True)
    
    if analyze_button:
        st.info("Funkcionalita analýzy není v základní verzi dostupná.")

with col2:
    st.header("Výsledky hodnocení")
    st.info("Zde se zobrazí výsledky po implementaci analytických funkcí.")

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center">
        <p>© 2025 EDUasistent | Základní verze</p>
    </div>
""", unsafe_allow_html=True)

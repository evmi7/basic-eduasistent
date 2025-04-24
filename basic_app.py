import streamlit as st

# IMPORTANT: set_page_config musí být první Streamlit příkaz v aplikaci
st.set_page_config(
    page_title="EduAssistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Zbytek importů
import pandas as pd
import numpy as np
# Přidejte další importy zde

# Název a popis aplikace
st.title("EduAssistant")
st.write("Welcome to EduAssistant, your learning companion!")

# Hlavní funkce aplikace
# ...

# Postranní panel
with st.sidebar:
    st.header("Options")
    option = st.selectbox("Choose a section", ["Home", "Study Materials", "Practice Quizzes", "Progress Tracker"])
    
    # Další komponenty postranního panelu
    st.subheader("Settings")
    # Nahrazení toggle za checkbox
    dark_mode = st.checkbox("Dark Mode")

# Podmíněný obsah podle vybrané možnosti
if option == "Home":
    st.header("Home")
    st.write("Welcome to the home page. Get started with your learning journey!")
    
elif option == "Study Materials":
    st.header("Study Materials")
    st.write("Access your study materials here.")
    
    # Příklad záložek pro předměty
    tabs = st.tabs(["Math", "Science", "History", "Languages"])
    
    with tabs[0]:
        st.subheader("Mathematics")
        st.write("Math content here")
        
    with tabs[1]:
        st.subheader("Science")
        st.write("Science content here")
    
    # A tak dále pro ostatní záložky
    
elif option == "Practice Quizzes":
    st.header("Practice Quizzes")
    st.write("Test your knowledge with these practice quizzes.")
    
    subject = st.selectbox("Select subject", ["Math", "Science", "History", "Languages"])
    difficulty = st.radio("Difficulty level", ["Easy", "Medium", "Hard"])
    
    if st.button("Start Quiz"):
        st.write(f"Starting a {difficulty} {subject} quiz...")
        
elif option == "Progress Tracker":
    st.header("Progress Tracker")
    st.write("Track your learning progress here.")
    
    # Příklad metrik pokroku
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Courses Completed", "5", "+1")
    with col2:
        st.metric("Average Score", "85%", "+2.5%")
    with col3:
        st.metric("Study Hours", "42", "+3")
    
    # Příklad grafu
    chart_data = pd.DataFrame(
        np.random.randn(20, 3),
        columns=['Math', 'Science', 'History']
    )
    st.line_chart(chart_data)

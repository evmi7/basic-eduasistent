import streamlit as st

# IMPORTANT: set_page_config must be the first Streamlit command used in your app
st.set_page_config(
    page_title="EduAssistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Rest of your imports
import pandas as pd
import numpy as np
# Add other imports here

# Your app title and description
st.title("EduAssistant")
st.write("Welcome to EduAssistant, your learning companion!")

# Main app functionality goes below
# ...

# Example sidebar
with st.sidebar:
    st.header("Options")
    option = st.selectbox("Choose a section", ["Home", "Study Materials", "Practice Quizzes", "Progress Tracker"])
    
    # Additional sidebar components
    st.subheader("Settings")
    dark_mode = st.toggle("Dark Mode")

# Conditional content based on selected option
if option == "Home":
    st.header("Home")
    st.write("Welcome to the home page. Get started with your learning journey!")
    
elif option == "Study Materials":
    st.header("Study Materials")
    st.write("Access your study materials here.")
    
    # Example tabs for subjects
    tabs = st.tabs(["Math", "Science", "History", "Languages"])
    
    with tabs[0]:
        st.subheader("Mathematics")
        st.write("Math content here")
        
    with tabs[1]:
        st.subheader("Science")
        st.write("Science content here")
    
    # And so on for other tabs
    
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
    
    # Example progress metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Courses Completed", "5", "+1")
    with col2:
        st.metric("Average Score", "85%", "+2.5%")
    with col3:
        st.metric("Study Hours", "42", "+3")
    
    # Example chart
    chart_data = pd.DataFrame(
        np.random.randn(20, 3),
        columns=['Math', 'Science', 'History']
    )
    st.line_chart(chart_data)

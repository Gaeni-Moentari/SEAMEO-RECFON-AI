from AI_Component.Crew import *
from AI_Component.validator.validator import *
import Component.Logo as Img
import streamlit as st
import time

# Helper function to check if a question is nutrition-related
def check_nutrition_related(question):
    """
    Simple check for nutrition-related keywords
    This is a fallback in case the RECFON validation fails
    """
    nutrition_keywords = [
        "seameorecfon","recfon","makanan", "gizi", "nutrisi", "sehat", "diet",
        "food", "nutrition", "healthy", "diet", "vegetable", "fruit",
        "vitamin", "mineral", "protein", "karbohidrat", "carbohydrate",
        "lemak", "fat", "sayur", "buah"
    ]
    
    question_lower = question.lower()
    for keyword in nutrition_keywords:
        if keyword in question_lower:
            return True
    
    return False

# Set page config (harus di paling atas)
Img.set_page_config(
    page_title="SEAMEO RECFON AI - NutriBot",
    page_icon="./Image/recfon.png",
    layout="wide"
)

# Initialize session state for chat history if it doesn't exist
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = ""

Img.image(["./Image/gema.png", "./Image/seameo.png", "./Image/recfon.png"])
st.title("SEAMEO RECFON AI")
st.write("Thinking about healthy menus for school children? Or want to know why vegetables are important? NutriBot has all the answers. This AI loves to talk about nutrition, healthy food, and simple healthy living.")
st.write("Koordinator Gatot HP - www.gaeni.org ")
input = st.text_input("Enter your question")
lang = "english"
submit = st.button("Start Search")

if submit:
    # Add the current question to chat history
    if st.session_state.chat_history:
        st.session_state.chat_history += f"\nUser: {input}"
    else:
        st.session_state.chat_history = f"User: {input}"
    
    # Validasi pertanyaan dengan validator yang sudah diperbarui
    validation_result = recfon_validator(input, st.session_state.chat_history)
    
    # Cek apakah pertanyaan valid (baik untuk RECFON atau nutrisi umum)
    if validation_result["is_recfon_context"] or check_nutrition_related(input):
        # Jika valid, lanjutkan ke proses utama
        with st.spinner('Recfon AI is thinking... Please wait'):
            # Show progress bar with realistic timing
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Simulate processing steps
            status_text.text('🔍 Analyzing your question...')
            progress_bar.progress(25)
            time.sleep(0.5)
            
            # Show different message based on context
            if validation_result["is_recfon_context"]:
                status_text.text('🧠 Processing SEAMEO RECFON knowledge...')
            else:
                status_text.text('🧠 Processing nutritional knowledge...')
            progress_bar.progress(50)
            time.sleep(0.5)
            
            status_text.text('📚 Generating response...')
            progress_bar.progress(75)
            
            # Pass chat history to the crew
            result = RecfonCrew(input, lang, st.session_state.chat_history).generalCrew()
            
            status_text.text('✅ Complete!')
            progress_bar.progress(100)
            time.sleep(0.3)
            
            # Clean up progress indicators
            progress_bar.empty()
            status_text.empty()
            
            # Add the response to chat history
            st.session_state.chat_history += f"\nAI: {result}"
        
        st.markdown(result)
    else:
        # Jika tidak valid, tampilkan pesan kesalahan
        st.error("Pertanyaan Anda tidak berkaitan dengan topik SEAMEO RECFON atau makanan dan gizi. Silakan ajukan pertanyaan yang relevan.")

import streamlit as st

def show_welcome():
    st.markdown(
        """
        <style>
        .welcome-title {
            font-size: 48px;
            font-weight: 900;
            color: #2e86de;
            text-align: center;
            margin-top: 30px;
        }
        .welcome-subtitle {
            font-size: 22px;
            color: #34495e;
            text-align: center;
            margin-bottom: 30px;
        }
        .welcome-container {
            background: linear-gradient(135deg, #f9f9f9 0%, #d0e8f2 100%);
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
            max-width: 800px;
            margin-left: auto;
            margin-right: auto;
        }
        </style>

        <div class="welcome-container">
            <h1 class="welcome-title">🦷 Welcome to Dentistry Stage 4! 🦷</h1>
            <p class="welcome-subtitle">Your journey to becoming a dental expert starts here. Let’s learn, practice, and succeed together! 💪✨</p>
            <img src="https://images.unsplash.com/photo-1588776814546-44ff6a7e8d3b?auto=format&fit=crop&w=900&q=80" style="width: 100%; border-radius: 10px; margin-top: 20px;" />
            <p style="text-align: center; font-style: italic; margin-top: 10px;">Your Journey Starts Here</p>
        </div>
        """,
        unsafe_allow_html=True
    )

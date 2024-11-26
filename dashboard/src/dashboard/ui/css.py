import streamlit as st

def apply_css():

    # Set background using custom CSS
    st.markdown(f"""
    <style>
        /* Reset default Streamlit styles */
        #root > div:first-child {{
            background-color: transparent;
        }}
        /* Sidebar container */
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #311579,#403699) !important;
            padding: 0;
            min-width: 300px;
        }}

        .stApp {{
        background: linear-gradient(to right, #140a31, #22264e);
        min-height: 100vh;
        }}


        .main .block-container {{
            background: transparent !important;
            padding: 0;
            margin-left: 0 !important;  /* Adds negative margin to move left */
            position: relative;   /* Ensures proper positioning */
            width: 100% !important  /* Maintains container width */
        }}

        /* Message cards */
        [data-testid="stChatMessage"] {{
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            margin: 2rem 0 !important;  /* Increased margin */
            padding: 1rem;
            max-width: 900px;
            width: 90%;  /* Added width constraint */
            position: relative;
            margin_left: 50px !important;
            text-align: left !important;
            clear: both !important;
        }}


        .chat-card {{
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;

        }}
        [data-testid="stChatMessage"] {{
            font-size: 19px !important;
        }}


        .stTextInput > div > div > input {{
            background-color: rgba(0, 0, 0, 0.2);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 15px;
            border-radius: 8px;

        }}

        /* Chat input */
        .stChatInput {{
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            width: 90%;
            max-width: 1000px;
        }}

        .stChatInput > div > div > input {{
            background: #334063 !important; 
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: white !important;  /* Set the text color to white */
            border-radius: 8px;
            margin: 1rem 0;
            padding: 1.2rem;

        }}

        .stChatInput > div > div > input::placeholder {{
            color: rgba(255, 255, 255, 0) !important;

        }}

        /* Text colors */
        p, h1, h2, h3, h4, h5, h6 {{
            color: white !important;
        }}

        /* Scrollbar styling */
        ::-webkit-scrollbar {{
            width: 8px;
        }}

        ::-webkit-scrollbar-track {{
            background: transparent;
        }}

        ::-webkit-scrollbar-thumb {{
            background: rgba(255, 255, 255, 0.2);
            border-radius: 4px;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: rgba(255, 255, 255, 0.3);
        }}
    </style>
    """, unsafe_allow_html=True)

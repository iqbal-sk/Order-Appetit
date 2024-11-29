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
            width: calc(300px+0%);
        }}

        .stApp {{
        background: linear-gradient(to right, #140a31, #22264e);
        min-height: 100vh;
        }}


        .main .block-container {{
            background: transparent !important;
            padding: 0;
            margin-left: 0% !important;  /* Adds negative margin to move left */
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
            max-width: 800px;
            width: 100%;  /* Added width constraint */
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
            font-size: 18px !important;
        }}


        /* Chat input */
        .stChatInput {{
            position: fixed;
            bottom: 2vh;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(255, 255, 255, 0.1);
            width:1200px
            max-width: 80px;
            margin: 0;
            padding: 0 0px;
            display: flex;
            font-color:white;
        }}
        div[data-testid="stChatInput"] button {{
            background: #334063 !important;
            border-radius: 12px;
            width: 40px;
            height: 40px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }}

        div[data-testid="stChatInput"] button:hover {{
            background: rgba(75, 59, 138, 0.8) !important;
            border-color: rgba(255, 255, 255, 0.4);
            transform: scale(1.05);
            box-shadow: 0 0 15px rgba(255, 255, 255, 0.1);
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
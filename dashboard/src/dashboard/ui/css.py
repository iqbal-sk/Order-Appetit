import streamlit as st

def apply_css():
    # Custom CSS for just the chat input
    st.markdown("""
    <style>
        /* Chat input container styling */
        .stTextInput {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            width: 50%;
        }
        /* Target Streamlit's specific input container */
        [data-testid="stTextInput"] > div > div > input {
            outline: none !important;
            box-shadow: none !important;
            border-color: rgba(255, 255, 255, 0.2) !important;
        }

        /* Handle the focus state */
        [data-testid="stTextInput"] > div > div > input:focus {
            box-shadow: none !important;
            border-color: rgba(255, 255, 255, 0.5) !important;
            outline: none !important;
        }

        /* Remove any residual outlines */
        div[data-testid="stTextInput"] {
            outline: none !important;
        }

        /* Target the specific container class */
        .stTextInput > div {
            outline: none !important;
            border: none !important;
        }

        /* Input field styling */
        .stTextInput > div > div > input {
            background:#334063 !important; 
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 12px !important;
            color: white !important;
            padding: 15px 20px !important;
            font-size: 18px !important;
            backdrop-filter: blur(8px);
            transition: all 0.3s ease;
        }
        .stTextInput > div > div > input:hover {
            border-color: rgba(255, 255, 255, 0.4) !important;
            box-shadow: 0 0 15px rgba(255, 255, 255, 0.1) !important;
            transform: scale(1);
        }
        .stTextInput > div > div > input:focus {
            border-color: rgba(255, 255, 255, 0.5) !important;
            box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.2) !important;
            background: #334063  !important;
        }
        /* Input placeholder styling */
        .stTextInput > div > div > input::placeholder {
            color: rgba(255, 255, 255, 0.5);
        }


        /* Button container */
        .button-container {
            position: fixed;
            right: 22%;
            bottom: 0px;
            transform: translateY(-50%);

        }

        /* Send button styling */
        .send-button {
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
        }

        .send-button:hover {
            background: rgba(75, 59, 138, 0.8) !important;
            border-color: rgba(255, 255, 255, 0.4);
            transform: scale(1.05);
            box-shadow: 0 0 15px rgba(255, 255, 255, 0.1);
        }

        /* Paper plane icon */
        .send-icon {
            color: white;
            transform: rotate(45deg);
            font-size: 20px;
            transition: all 0.3s ease;
        }

        .send-button:hover .send-icon {
            transform: rotate(45deg) translateX(2px);
            color: rgba(255, 255, 255, 0.9);
        }
    </style>


    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">

    <!-- HTML Structure -->
    <div class="button-container">
        <button class="send-button">
            <span class="send-icon"><i class="fas fa-paper-plane"></i></span> <!-- Send icon -->
        </button>
    </div>
    """, unsafe_allow_html=True)

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
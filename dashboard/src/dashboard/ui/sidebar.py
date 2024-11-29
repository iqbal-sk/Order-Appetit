import streamlit as st

from dashboard.src.dashboard.utils.chat_utils import delete_thread, truncate_message, switch_thread, create_new_thread


# Add this CSS for the bin icon styling
custom_icon_css = """
<style>

.thread-container {
    margin: 0px !important;
    padding: 0px !important;
}

.stButton {
    margin: 0px !important;
    padding: 0px !important;
}

.stButton > button {
    margin: 1px !important;
    padding: 8px !important;
    width: 100% !important;
}
.stButton:first-child > button {
    margin-bottom: 2px !important;
}

[data-testid="column"] {
    padding: 0px !important;
    margin: 0px !important;
}

.element-container {
    margin: 0px !important;
    padding: 0px !important;
}
div[data-testid="stVerticalBlock"] > div {
    gap: 0rem !important;
    padding: 0rem !important;
}

div[class*="stVerticalBlock"] {
    margin: 3px !important;
    gap: 0rem !important;
    padding: 0rem !important;
}

.stButton,
.stMarkdown,
div[data-testid="column"] {
    margin: 0px !important;
    padding: 0px !important;
}

.stButton > button {
    margin: 0px !important;
    padding: 8px !important;
}

.element-container,
.stMarkdown > div {
    margin: 0px !important;
    padding-top: 0px !important;
    padding-bottom: 0px !important;
}
/* Target the button text directly */
[data-testid="stButton"] button p {
    font-size: 0.9rem !important;
}
</style>
"""



def render_sidebar():
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Radley&display=swap');
            .sidebar-title {
                font-family: 'Radley', serif !important;
                text-align: center !important;
                padding: 0rem 0 !important;
                font-size: 3rem !important;
                color:  white !important;
                margin-bottom: 0.5rem!important;
            }
            /* Navigation menu */
            .support-nav-item {
                position: relative;
            }
            .support-nav-item .support-dropdown {
                display: block;
                position: absolute;
                left: 0;
                background-color:#181038!important;
                padding: 10px;
                width: 102%;
                z-index: 1000;
                border-radius: 8px;
                color: white !important;
                text-align: center !important;
                visibility: hidden;
                opacity: 0;
                transition: opacity 0.3s, visibility 0s linear 1s;
            }
            .support-nav-item:hover .support-dropdown {
                visibility: visible;
                opacity: 1;
                transition-delay: 1s;
            }
            .email-item {
                padding: 8px;
                margin: 5px 0;
                border-bottom: 1px solid #eee;
            }
             /* Chat list section */
            .chat-list-header {
                padding: 1px 10px;
                color: rgba(255, 255, 255, 0.6);
                align-items: center;
                font-size: 1.2rem;
                width: 300px;
                font-weight: 100;
            }

            /* User profile section */
            .user-profile {
                position: fixed;
                bottom: 20px;
                left: 10px;
                width: 230px;
                padding: 16px 24px;
                background: rgba(0, 0, 0, 0.2);
                display: flex;
                align-items: left;
                gap: 12px;
                border-radius: 8px;
                z-index: 100;
            }
            .user-profile:hover {
                background: rgba(0, 0, 0, 0.3);
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
            }
            .user-avatar {
                width: 32px;
                height: 32px;
                border-radius: 50%;
                background-image: url('https://pbs.twimg.com/profile_images/1557071011467739136/mBfyJP5B_400x400.jpg');
                background-size: cover;
                background-position: center;
            }

            .user-info {
                flex-grow: 1;
            }

            .user-name {
                color: white;
                font-size: 1rem;
                align-items: center;
            }

            .user-email {
                color: rgba(255, 255, 255, 0.6);
                font-size: 1rem;
                align-items: center;
            }
            .stButton > button {
                margin: 0px;
                padding: 1px 10px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                color: white;
                text-align: center;
                cursor: pointer;
                transition: background 0.3s ease;
                width: calc(100% - 10px);
                border: none;
                gap=1px;
            }

            .stButton > button:hover {
                background: rgba(255, 255, 255, 0.2);
            }

            /* Delete button */
            .delete-btn {
                background: transparent;
                border: none;
                padding: 4px;
                cursor: pointer;
                display: flex;
                align-items: center;
            }
            .delete-icon {
                width: 16px;
                height: 16px;
                fill: white;
                opacity: 0.7;
                transition: fill 0.3s ease;
            }
            .delete-btn:hover .delete-icon {
            opacity: 1;
            fill: #ff3b30;
            }

            /* Section header */
            .section-header {
                color: white;
                font-size: 20px;
                margin: 24px 0 16px 0;
                padding: 0 12px;
            }
            /* Optional: Add hover effect */
            .sidebar-title:hover {
                color: rgba(255, 255, 255, 0.8) !important;
            }


        </style>
        <div class="sidebar-title">AppetiQ</div>
        """,
        unsafe_allow_html=True
    )
    # sidebar items
    st.markdown("""
                <div class="nav-item">
                    <a href="https://orderappetit.com/" style="text-decoration: none; color: inherit; display: flex; align-items: center;">
                        <img src="https://orderappetit.com/static/media/buffalo.dce0a965.png" style="width: 30px; height: 30px; margin-right: 8px;">
                        Order Appetit
                    </a>
                </div>
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
                <div class="nav-item support-nav-item">
                    <div style="display: flex; align-items: center; padding: 8px;">
                        <i class="fa-solid fa-headset" style="width: 30px; height: 30px; margin-right: 8px; display: flex; align-items: center; justify-content: left;"></i>
                        <span style="display: inline-block; vertical-align: left;">Support</span>
                    </div>
                    <div class="support-dropdown">
                    <div> <h1>Contact</h1></div>
                    <div class="email-item"><a href="mailto:mahammad@buffalo.edu">mahammad@buffalo.edu</a></div>
                    <div class="email-item"><a href="mailto:vduggemp@buffalo.edu">vduggemp@buffalo.edu</a></div>
                    <div class="email-item"><a href="mailto:saishiri@buffalo.edu">saishiri@buffalo.edu</a></div>
                    <div class="email-item"><a href="mailto:vkaturu@buffalo.edu">vkaturu@buffalo.edu</a></div>
                </div>
                </div>
            """, unsafe_allow_html=True)
    # Chat List Section
    st.markdown('<div class="chat-list-header">Chat List</div>', unsafe_allow_html=True)

    # Functions for thread management
    st.markdown("""
                <div class="user-profile">
                    <a href="https://www.buffalo.edu" style="text-decoration: none; color: inherit;">
                        <div style="display: flex; align-items: center; padding: 12px;">
                            <div class="user-avatar" style="margin-right: 16px;"></div>
                            <div class="user-info">
                                <div class="user-name">Created by UB</div>
                                <div class="user-email">@buffalo.edu</div>
                            </div>
                        </div>
                    </a>
                </div>
            """, unsafe_allow_html=True)

    # Apply custom styling
    st.markdown(custom_icon_css, unsafe_allow_html=True)

    if st.button("+New Thread", key="new_thread_btn", use_container_width=True):
        create_new_thread()

    sorted_threads = sorted(st.session_state.chat_history.items(), key=lambda x: float(x[0]), reverse=True)
    for thread_id, thread in sorted_threads:
        try:
            first_message = thread[0]["content"] if thread else "No messages yet"
            first_message = truncate_message(first_message)
        except (IndexError, KeyError, TypeError):
            first_message = "No messages yet"

        st.markdown('<div class="thread-container">', unsafe_allow_html=True)
        col1, spacer, col2 = st.columns([5.5, 0.5, 1])
        with col1:
            st.markdown('<div class="thread-button">', unsafe_allow_html=True)
            if st.button(f"{first_message}", key=f"switch_thread_{thread_id}"):
                switch_thread(thread_id)
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="delete-button">', unsafe_allow_html=True)
            if st.button("⌫", key=f"delete_thread_{thread_id}"):
                delete_thread(thread_id)
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

import streamlit as st

from dashboard.src.dashboard.utils.chat_utils import delete_thread, truncate_message, switch_thread, create_new_thread


# Add custom CSS for the button styling
custom_button_css = """
<style>
.stButton > button {
    margin: 12px 24px;
    padding: 1px 10px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    color: white;
    text-align: center;
    cursor: pointer;
    transition: background 0.3s ease;
    width: calc(100% - 48px);
    border: none;
}

.stButton > button:hover {
    background: rgba(255, 255, 255, 0.2);
}

</style>
"""

# Add this CSS for the bin icon styling
custom_icon_css = """
<style>
.thread-container {
    display: flex;
    align-items: center;
    gap: 0;
    padding: 1px 8px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    margin: 0 0 1px 0;
}

.thread-button > button {
    width:calc(100% - 48px);
    text-align: left !important;
    background: transparent !important;
    border: none !important;
    color: white !important;
    padding: 0 !important;
    margin: 0 !important;
}

.delete-button > button {
    background: transparent !important;
    border: none !important;
    color: rgba(255, 255, 255, 0.6) !important;
    padding: 0 !important;
    min-width: auto !important;
    margin: 0 !important;
    align: left !important;
}


.delete-button > button:hover {
    color: white !important;
}
/* Remove gaps between threads */
.element-container {
    margin: 0 !important;
    padding: 0 !important;
}
* Modify column layout */
[data-testid="column"] {
    padding: 0 !important;
    gap: 0 !important;
}

/* Remove default Streamlit button styling */
.stButton {
    margin: 0 !important;
}
/* Remove gaps in markdown elements */
.stMarkdown {
    margin: 0 !important;
    padding: 0 !important;
}
</style>
"""



def render_sidebar():
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Radley&display=swap');

            .css-1d391kg {  /* Sidebar background */
                background: linear-gradient(to down, #311579, #5865c9);
            }

            .sidebar-title {
                font-family: 'Radley', serif !important;
                text-align: center !important;
                padding: 0rem 0 !important;
                font-size: 3rem !important;
                color:  white !important;
                margin-bottom: 0.5rem!important;
            }
            /* Navigation menu */
            .nav-item {
                padding: 6px 12px;
                color: rgba(255, 255, 255, 0.8);
                display: flex;
                font-size: 1.2rem !important;
                align-items: center;
                gap: 1px;
                transition: background 0.3s ease;
            }
            .nav-item:hover {
            background: rgba(255, 255, 255, 0.1);
            }
             /* Chat list section */
            .chat-list-header {
                padding: 1px 100px;
                color: rgba(255, 255, 255, 0.6);
                align-items: center;
                font-size: 1.5rem;
                width: 300px;
                font-weight: 100;

            }


            /* User profile section */
            .user-profile {
                position: fixed;
                bottom: 20px;
                left: 16px;
                width: 250px;
                padding: 16px 24px;
                background: rgba(0, 0, 0, 0.2);
                display: flex;
                align-items: center;
                gap: 12px;
                border-radius: 8px;
                z-index: 100;
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
                <div class="nav-item">
                    <div style="display: flex; align-items: center; padding: 8px;">
                        <i class="fa-solid fa-headset" style="width: 30px; height: 30px; margin-right: 8px; display: flex; align-items: center; justify-content: left;"></i>
                        <span style="display: inline-block; vertical-align: left;">Support</span>
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
    st.markdown(custom_button_css, unsafe_allow_html=True)
    st.markdown(custom_icon_css, unsafe_allow_html=True)

    # Create functional button with custom styling
    if st.button("+New Thread", key="new_thread_btn", use_container_width=True):
        create_new_thread()

    sorted_threads = sorted(st.session_state.chat_history.items(), key=lambda x: float(x[0]), reverse=True)
    for thread_id, thread in sorted_threads:
        try:
            first_message = thread['messages'][0]["content"] if thread else "No messages yet"
            first_message = truncate_message(first_message)
        except (IndexError, KeyError, TypeError):
            first_message = "No messages yet"

        st.markdown('<div class="thread-container">', unsafe_allow_html=True)
        col1, col2 = st.columns([6, 1])
        with col1:
            st.markdown('<div class="thread-button">', unsafe_allow_html=True)
            if st.button(f"{first_message}", key=f"switch_thread_{thread_id}"):
                switch_thread(thread_id)
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="delete-button">', unsafe_allow_html=True)
            if st.button("🗑️", key=f"delete_thread_{thread_id}"):
                delete_thread(thread_id)
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

import streamlit as st
from streamlit_option_menu import option_menu
import google.generativeai as genai
from nutritional_planner import nutritional_planner_ui
from workout_planner import workout_planner_ui
from mhs_chatbot import mental_health_chatbot_ui
from utils import init_db, validate_username, validate_password, verify_user, insert_user

# Generative AI
genai.configure(api_key=st.secrets["GEMINI"])
model = genai.GenerativeModel("gemini-2.0-flash")

# NutritionIX credentials
app_id = st.secrets["NUTRITIONIX_APP_ID"]
api_key = st.secrets["NUTRITIONIX_API_KEY"]

st.set_page_config(
    page_title="MindFit",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide streamlit header and footer
hide_streamlit_style = """
    <style>
    header {visibility: hidden;}
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    div.block-container {padding-top: 1rem;}
    button {
        width: 50%;
        padding: 0.5rem;
        border-radius: 5px;
        border: none;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    div.css-1n76uvr {width: 100%;}

    /* Fix password input styling */
    div[data-baseweb="input"] {
        justify-content: flex-start !important;
    }
    .stTextInput div[data-baseweb="input"] {
        text-align: left !important;
    }
    .stTextInput div[data-baseweb="base-input"] {
        justify-content: flex-start !important;
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

def main():
    init_db()
    
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'user' not in st.session_state:
        st.session_state['user'] = None
    if 'diet_plan' not in st.session_state:
        st.session_state['diet_plan'] = None
    if 'bmi' not in st.session_state:
        st.session_state['bmi'] = None
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "Login"

    if not st.session_state['logged_in']:
        # for centering the login content
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<h1 style='text-align: center;'>🏋️‍♂️ MindFit</h1>", unsafe_allow_html=True)            
            st.markdown("<p style='text-align: center; font-size: 1.2em;'>Your Journey to Wellness Begins Here</p>", unsafe_allow_html=True)
            # Improved Login Page Design
            st.markdown("<br>", unsafe_allow_html=True)
            tab1, tab2 = st.tabs(["Login", "Sign Up"])
            
            with tab1:
                st.markdown("<br>", unsafe_allow_html=True)
                username = st.text_input("Username", placeholder="Enter your username", key="login_username")
                password = st.text_input("Password", placeholder="Enter your password", type="password", key="login_password")
                
                if st.button("Login", key="login_button", use_container_width=True):
                    if not username or not password:
                        st.error("Please enter both username and password.")
                    else:
                        with st.spinner("Verifying credentials..."):
                            user = verify_user(username, password)
                            if user:
                                st.session_state['user'] = {'id': user[0], 'username': username}
                                st.session_state['logged_in'] = True
                                st.success("Login successful!")
                                st.rerun()
                            else:
                                st.error("Invalid credentials. Please try again.")
            
            with tab2:
                st.markdown("<br>", unsafe_allow_html=True)
                new_username = st.text_input("Choose Username", placeholder="Pick a unique username", key="signup_username")
                new_password = st.text_input("Create Password", placeholder="Enter a strong password", type="password", key="signup_password")
                confirm_password = st.text_input("Confirm Password", placeholder="Re-enter your password", type="password", key="confirm_password")
                
                if st.button("Sign Up", key="signup_button", use_container_width=True):
                    if not validate_username(new_username):
                        st.error("Username must be 3-20 characters long and contain only letters, numbers, and underscores.")
                    elif not validate_password(new_password):
                        st.error("Password must be at least 8 characters long and contain uppercase, lowercase, and numbers.")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match.")
                    else:
                        with st.spinner("Creating account..."):
                            if insert_user(new_username, new_password):
                                st.success("Account created successfully! Please log in.")
                                st.session_state.active_tab = "Login"
                            else:
                                st.error("Username already exists. Please choose another.")
    
    else:
        def nav_to_diet():
            st.session_state.menu_selection = "Diet"
            
        def nav_to_workout():
            st.session_state.menu_selection = "Workout"
            
        def nav_to_chat():
            st.session_state.menu_selection = "Health Chat"

        if 'menu_selection' not in st.session_state:
            st.session_state.menu_selection = "Home"

        options = ["Home", "Diet", "Workout", "Health Chat", "Logout"]
        current_index = options.index(st.session_state.menu_selection)

        selected = option_menu(
            menu_title=None,
            options=["Home", "Diet", "Workout", "Health Chat", "Logout"],
            icons=["house", "book", "person", "chat-dots", "box-arrow-right"],
            menu_icon="cast",
            default_index=current_index,
            orientation="horizontal",
            key='menu_selection', 
            styles={
                "container": {"padding": "0!important"},
                "icon": {"color": "orange", "font-size": "25px"},
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "center",
                    "margin": "0px",
                    "--hover-color": "#eee",
                },
                "nav-link-selected": {"background-color": "#2c3e50"},
            }
        )
        
        if selected == "Home":
            # Sidebar for Home page
            sidebar_style = """
                <style>
                section[data-testid="stSidebar"] > div {
                    padding-top: 0 !important;
                    margin-top: 0 !important;
                }
                section[data-testid="stSidebar"] > div > div {
                    padding-top: 0 !important;
                    margin-top: 0 !important;
                }
                section[data-testid="stSidebar"] div:has(img) {
                    padding-top: 0 !important;
                    margin-top: -7px !important;
                }
                [data-testid="collapsedControl"] {
                    display: none !important;
                }
                </style>
            """
            st.markdown(sidebar_style, unsafe_allow_html=True)
            st.sidebar.markdown('<div style="margin-top: -100px;"></div>', unsafe_allow_html=True)
            st.sidebar.image("not2.png", width=265, use_container_width=False)
            st.sidebar.header("About MindFit")
            st.sidebar.info(
                "MindFit is your AI-powered health & wellness companion. "
                "Get personalized diet plans, workout routines, and health guidance — all in one place."
            )
            st.sidebar.write("**Quick Navigation**")
            st.sidebar.write("""
            - 🥗 **Diet** — Personalized meal plans
            - 🏋️ **Workout** — Custom exercise routines
            - 🤖 **Health Chat** — AI health assistant
            """)

            username = st.session_state.get('user', {}).get('username', 'Guest')
            st.markdown(
                f"<h1 style='text-align: center; color: #2c3e50;'>Welcome to MindFit, {username}! 👋</h1>",
                unsafe_allow_html=True
            )
            st.text("Welcome to your personalized journey toward better health and wellness! At NutriFit, we merge the power of advanced AI technology with your individual preferences and needs to craft tailored solutions just for you. From personalized diet plans and thoughtfully designed workout routines to actionable health insights, we are committed to empowering you to take charge of your health. Our mission is to make fitness and nutrition not only accessible but also sustainable and seamlessly integrated into your lifestyle. MindFit is here to support your unique path to a healthier, happier you!")
            st.text("With MindFit, we go beyond generic solutions to provide a truly personalized experience. Whether you're striving for fitness goals, managing specific health conditions, or simply looking to adopt a healthier lifestyle, our platform adapts to your needs. By incorporating eco-friendly practices and culturally relevant options, we ensure that your journey toward better health is sustainable and relatable. NutriFit is more than just a tool—it's your partner in achieving a balanced, fulfilling, and health-conscious life. Let us help you transform your goals into lasting habits!")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.info("🥗 **Diet Planner:** Our planner creates personalized meal plans that align with your health goals, dietary preferences, and lifestyle. Whether you’re looking to lose weight, gain muscle, or maintain a balanced diet, we factor in your preferences, allergies, and budget to ensure the recommendations are practical and sustainable.")
                st.button("Go to Diet Planner", on_click=nav_to_diet, use_container_width=True)
            with col2:
                st.info("🏋️ **Workout Plan Generator:** Build a workout routine that matches your fitness level, goals, and time availability. Whether you're a beginner or an experienced fitness enthusiast, our generator provides customizable plans, including equipment-based and home-friendly workouts, to keep you motivated and on track.")
                st.button("Go to Workout Planner", on_click=nav_to_workout, use_container_width=True)
            with col3:
                st.info("🤖 **Health Chatbot:** Get round-the-clock assistance with our intelligent chatbot. It provides quick answers to your health-related questions, offers actionable advice, and guides you through nutrition and fitness best practices to keep you informed and inspired. (Please note, this is not intended to replace professional mental health guidance.)")
                st.button("Go to Health Chat", on_click=nav_to_chat, use_container_width=True)
        
        elif selected == "Diet":
            nutritional_planner_ui(model, app_id, api_key)
        
        elif selected == "Workout":
            workout_planner_ui(model)
        
        elif selected == "Health Chat":
            mental_health_chatbot_ui(model)
        
        elif selected == "Logout":
            st.session_state['logged_in'] = False
            st.rerun()

if __name__ == "__main__":
    main()
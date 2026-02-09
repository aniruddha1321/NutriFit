import streamlit as st
from utils import create_pdf

def generate_fitness_tip(model):
    prompt = "Generate a short, motivating fitness tip."
    response = model.generate_content(prompt)
    return response.text

def workout_planner_ui(model):
    # session states
    if 'workout_plan' not in st.session_state:
        st.session_state.workout_plan = None
    
    if 'fitness_tip' not in st.session_state:
        try:
            prompt = "Generate a short, motivating fitness tip."
            st.session_state.fitness_tip = model.generate_content(prompt).text
        except Exception:
            st.session_state.fitness_tip = "Stay consistent! Small daily efforts lead to big results over time. 💪"

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
        </style>
    """
    st.markdown(sidebar_style, unsafe_allow_html=True)

    st.sidebar.markdown('<div style="margin-top: -100px;"></div>', unsafe_allow_html=True)

    st.sidebar.image(
        "not2.png",
        width=265,
        use_container_width=False
    )

    st.markdown(
        '<h2 class="page-title" style="text-align: center; margin-top: -30px;">Workout Plan Generator 🏋️</h2>',
        unsafe_allow_html=True
    )
    
    st.sidebar.header("Fitness Tip of the Day")
    st.sidebar.info(st.session_state.fitness_tip)

    st.sidebar.write("**Guidelines for using the Workout Plan Generator**")

    st.sidebar.write("""
    1. **Fill All Fields**: Complete all input sections.
    2. **Health Conditions**: Mention any health issues for safer plans.
    3. **Be Specific**: Provide accurate info for personalized results.
    4. **Select Preferences**: Choose workout type, duration, and equipment.
    5. **Review and Adjust**: Verify your plan and make adjustments.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fitness_level = st.selectbox("Fitness Level", ["Beginner", "Intermediate", "Advanced"])
        age = st.number_input("Age", min_value=10, max_value=120)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        height = st.number_input("Height (cm)", min_value=100, max_value=250)
    
    with col2:
        weight = st.number_input("Weight (kg)", min_value=30, max_value=200)
        workout_type = st.selectbox(
            "Workout Focus",
            ["Strength Training", "Weight Loss", "Muscle Gain", "Endurance", "Flexibility"]
        )
        equipment = st.selectbox(
            "Available Equipment",
            ["No Equipment", "Basic Home Equipment", "Full Gym Access"]
        )
        health_conditions = st.text_input("Any health conditions or injuries?")
    
    time_commitment = st.slider("Time per session (minutes)", 10, 120, 30)
    
    if st.button("Generate Workout Plan", type="primary"):
        if all([fitness_level, age, gender, height, weight, workout_type]):
            prompt = (
                f"Create a detailed workout plan with:\n"
                f"Fitness Level: {fitness_level}\n"
                f"Age: {age}\n"
                f"Gender: {gender}\n"
                f"Height: {height}cm\n"
                f"Weight: {weight}kg\n"
                f"Focus: {workout_type}\n"
                f"Equipment: {equipment}\n"
                f"Time: {time_commitment} minutes\n"
                f"Health Conditions: {health_conditions}\n\n"
                f"Include:\n"
                f"1. Warm-up routine\n"
                f"2. Main exercises with sets, reps, and rest periods\n"
                f"3. Cool-down stretches\n"
                f"4. Weekly progression plan\n"
                f"5. Safety tips and form cues"
            )
            
            with st.spinner("Creating your personalized workout plan..."):
                try:
                    st.session_state.workout_plan = model.generate_content(prompt).text
                except Exception as e:
                    st.error(f"⚠️ Could not generate workout plan. API quota may be exhausted. Please try again later.\n\nError: {e}")
    
    # always display the workout plan if it exists in session state            
    if st.session_state.workout_plan:
        st.success("Your workout plan is ready!")
        st.write(st.session_state.workout_plan)
        
        pdf = create_pdf(st.session_state.workout_plan, "workout_plan.pdf")
        st.download_button(
            "Download Workout Plan (PDF)",
            data=pdf,
            file_name="workout_plan.pdf",
            mime="application/pdf"
        )
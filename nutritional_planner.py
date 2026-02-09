import streamlit as st
from utils import create_pdf
import requests

# for bmi calculation
def calculate_bmi(weight, height):
    height_m = height / 100
    bmi = weight / (height_m ** 2)
    return round(bmi, 2)

# for bmi category
def get_bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 25:
        return "Normal weight"
    elif 25 <= bmi < 30:
        return "Overweight"
    else:
        return "Obese"

# for nutritional information
def get_nutritional_info(food_item, app_id, api_key):
    url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
    headers = {
        "x-app-id": app_id,
        "x-app-key": api_key,
        "Content-Type": "application/json"
    }
    body = {
        "query": food_item,
        "timezone": "US/Eastern"
    }
    
    response = requests.post(url, json=body, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data['foods']:
            food = data['foods'][0]
            return {
                "calories": food.get('nf_calories'),
                "protein": food.get('nf_protein'),
                "carbohydrates": food.get('nf_total_carbohydrate'),
                "fat": food.get('nf_total_fat')
            }
    return None

def nutritional_planner_ui(model, app_id, api_key):
    # sidebar logo
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

    hide_sidebar_button = """
    <style>
        [data-testid="collapsedControl"] {
            display: none !important;
        }
    </style>
    """
    st.markdown(hide_sidebar_button, unsafe_allow_html=True)
    st.sidebar.markdown('<div style="margin-top: -100px;"></div>', unsafe_allow_html=True)
    st.sidebar.image(
        "not2.png",
        width=265,
        use_container_width=False
    )

    # centering the title
    st.markdown(
        '<h2 class="page-title" style="text-align: center; margin-top: -50px;">🥗 Nutritional Planning</h2>',
        unsafe_allow_html=True
    )
    # st.write("Let's create your personalized diet plan!. Input your details, set your goals, and get a tailored meal plan designed to match your lifestyle and preferences. Start your journey to better health today!")

    # session state for diet plan
    if 'diet_plan' not in st.session_state:
        st.session_state.diet_plan = None
    
    # calorie counter sidebar
    with st.sidebar:
        st.write("Let's create your personalized diet plan!. Input your details, set your goals, and get a tailored meal plan designed to match your lifestyle and preferences. Start your journey to better health today!")
        st.markdown("""
            <h3 style="text-align: center;">Calorie Counter</h3>
        """, unsafe_allow_html=True)
        st.write("Get nutritional information for any food item:")
        food_item = st.text_input("Enter food item:", key="nutrition_input")
        
        if st.button("Get Nutritional Info"):
            if food_item:
                with st.spinner("Fetching nutritional information..."):
                    nutrition = get_nutritional_info(food_item, app_id, api_key)
                    if nutrition:
                        st.session_state.nutrition_info = {
                            'food': food_item,
                            'data': nutrition
                        }
    
    # display nutritional information
    if hasattr(st.session_state, 'nutrition_info'):
        with st.sidebar:
            st.write(f"**{st.session_state.nutrition_info['food'].title()}**")
            nutrition = st.session_state.nutrition_info['data']
            st.write(f"Calories: {nutrition['calories']} kcal")
            st.write(f"Protein: {nutrition['protein']} g")
            st.write(f"Carbohydrates: {nutrition['carbohydrates']} g")
            st.write(f"Fat: {nutrition['fat']} g")
    
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("Name")
        weight = st.number_input("Weight (kg)", min_value=1.0, step=0.1)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        activity_level = st.select_slider(
            "Activity Level",
            options=["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extra Active"]
        )
    
    with col2:
        age = st.number_input("Age", min_value=12, max_value=88)
        height = st.number_input("Height (cm)", min_value=50.0, step=0.1)
        diet_preference = st.selectbox("Diet Preference", ["Vegetarian", "Non-Vegetarian"])
        preferences = st.text_area("Any dietary restrictions or preferences?")
    


    if st.button("Generate Diet Plan", type="primary"):
        if all([name, age, height, weight, diet_preference]):
            bmi = calculate_bmi(weight, height)
            bmi_category = get_bmi_category(bmi)
            
            st.info(f"Your BMI is {bmi} ({bmi_category})")
            
            prompt = (
                f"Create a detailed, personalized diet plan for {name}:\n"
                f"Age: {age}\n"
                f"Gender: {gender}\n"
                f"BMI: {bmi} ({bmi_category})\n"
                f"Diet Preference: {diet_preference}\n"
                f"Activity Level: {activity_level}\n"
                f"Preferences/Restrictions: {preferences}\n\n"
                f"Include:\n"
                f"1. Daily caloric needs\n"
                f"2. Macro distribution\n"
                f"3. Meal-wise plan with portions\n"
                f"4. Healthy snack options\n"
                f"5. Foods to avoid\n"
                f"6. Hydration guidelines"
            )
            
            with st.spinner("Generating your personalized diet plan..."):
                try:
                    st.session_state.diet_plan = model.generate_content(prompt).text
                except Exception as e:
                    st.error(f"⚠️ Could not generate diet plan. API quota may be exhausted. Please try again later.\n\nError: {e}")
                
    if st.session_state.diet_plan:
        st.success("Your diet plan is ready!")
        st.write(st.session_state.diet_plan)
        
        pdf = create_pdf(st.session_state.diet_plan, "diet_plan.pdf")
        st.download_button(
            "Download Diet Plan (PDF)",
            data=pdf,
            file_name="diet_plan.pdf",
            mime="application/pdf"
        )
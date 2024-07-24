import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st

# Load dataset
data = pd.read_csv('D:/sv1/Recipe Dataset.csv')  # Make sure to provide the correct path to your dataset file

# Function to calculate similarity
def calculate_similarity(user_profile_values, data):
    data_values = data[['Calories', 'FatContent', 'CarbohydrateContent', 'ProteinContent']]
    data_values = (data_values - data_values.min()) / (data_values.max() - data_values.min())
    similarity = cosine_similarity([user_profile_values], data_values)
    data['Similarity'] = similarity[0]
    return data

# Streamlit app
st.title("Plate Pal")
st.write("Where AI meets your Appetite")

# User sign-in
st.sidebar.header("Sign In")
name = st.sidebar.text_input("Enter your name:")
if st.sidebar.button("Sign In"):
    st.session_state.user_info = {
        'name': name,
        'age': None,
        'sugar_level': None,
        'blood_pressure': None,
        'calories': None,
        'fat_content': None,
        'carb_content': None,
        'protein_content': None,
    }
    st.sidebar.success(f"Welcome, {name}!")

# Collect user information
if 'user_info' in st.session_state:
    user_info = st.session_state.user_info
    st.sidebar.subheader("User Information")
    user_info['age'] = st.sidebar.slider("Select your age:", 1, 100, 30)
    user_info['sugar_level'] = st.sidebar.slider("Enter your sugar level (mg/dL):", 1, 500, 80)
    user_info['blood_pressure'] = st.sidebar.slider("Enter your blood pressure (mmHg):", 1, 300, 120)
    user_info['calories'] = st.sidebar.slider("Enter your daily calorie intake:", 1, 5000, 2000)
    user_info['fat_content'] = st.sidebar.slider("Enter your daily fat intake (grams):", 1, 500, 70)
    user_info['carb_content'] = st.sidebar.slider("Enter your daily carbohydrate intake (grams):", 1, 500, 300)
    user_info['protein_content'] = st.sidebar.slider("Enter your daily protein intake (grams):", 1, 500, 50)

# Calculate similarity and recommend foods
if 'user_info' in st.session_state and st.sidebar.button("Get Recommendations"):
    user_profile_values = [
        user_info['calories'],
        user_info['fat_content'],
        user_info['carb_content'],
        user_info['protein_content']
    ]
    user_profile_values = [(x - min(user_profile_values)) / (max(user_profile_values) - min(user_profile_values)) for x in user_profile_values]
    
    recommended_foods = calculate_similarity(user_profile_values, data)
    recommended_foods = recommended_foods.sort_values(by='Similarity', ascending=False).head(5)
    st.subheader("Recommended Foods:")
    
    for i, (_, row) in enumerate(recommended_foods.iterrows(), 1):
        st.write(f"{i}. {row['Name']}")
        st.write("Recipe Instructions:")
        st.write(row['RecipeInstructions'])
        st.write("\n")

# Display user input
if 'user_info' in st.session_state:
    st.sidebar.subheader("User Input Summary:")
    st.sidebar.write(f"Name: {user_info['name']}")
    st.sidebar.write(f"Age: {user_info['age']}")
    st.sidebar.write(f"Sugar Level: {user_info['sugar_level']} mg/dL")
    st.sidebar.write(f"Blood Pressure: {user_info['blood_pressure']} mmHg")
    st.sidebar.write(f"Calories: {user_info['calories']}")
    st.sidebar.write(f"Fat Content: {user_info['fat_content']} grams")
    st.sidebar.write(f"Carbohydrate Content: {user_info['carb_content']} grams")
    st.sidebar.write(f"Protein Content: {user_info['protein_content']} grams")
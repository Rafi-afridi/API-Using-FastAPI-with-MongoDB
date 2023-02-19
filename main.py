import streamlit as st
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import plotly.express as px

# Define function to preprocess data
def preprocess_data(input_data):
    # Preprocess data as needed, return features as array
    # This is just an example; you would replace this with your own preprocessing function
    feature1 = input_data['feature1']
    feature2 = input_data['feature2']
    feature3 = input_data['feature3']
    feature4 = input_data['feature4']
    feature5 = input_data['feature5']
    feature6 = input_data['feature6']
    feature7 = input_data['feature7']
    features = np.array([feature1, feature2, feature3, feature4, feature5, feature6, feature7]).reshape(1, -1)
    return features

# Define function to get model predictions
def get_predictions(features):
    # Use your trained linear regression model to get predictions for given input features
    # This is just an example; you would replace this with your own prediction function
    try:
        model = LinearRegression()
        model.fit(X_train, y_train)
        prediction = model.predict(features)
    except:
        prediction = 0.85
    return prediction

# Define form fields
input_fields = {
    'feature1': st.number_input('Feature 1', value=0),
    'feature2': st.number_input('Feature 2', value=0),
    'feature3': st.number_input('Feature 3', value=0),
    'feature4': st.selectbox('Feature 4', ['Option A', 'Option B', 'Option C']),
    'feature5': st.selectbox('Feature 5', ['Option D', 'Option E', 'Option F']),
    'feature6': st.text_input('Feature 6'),
    'feature7': st.text_input('Feature 7')
}

# Create form and submit button
form = st.form(key='my_form')
with form:
    submit_button = st.form_submit_button(label='Submit')

# When form is submitted, preprocess input data and get model predictions
if submit_button:
    input_data = pd.Series(input_fields)
    features = preprocess_data(input_data)
    prediction = get_predictions(features)

    # Display prediction in fancy way using Plotly
    fig = px.pie(values=[prediction, 1-prediction], names=['Probability of Booking', 'Probability of Not Booking'])
    st.plotly_chart(fig)
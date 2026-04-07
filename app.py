import streamlit as st
st.title("My First Streamlit App")

st.write("Hello World!")

# Selection widgets
st.checkbox('Check me') 
st.button('Click me')
st.radio('Pick your gender', ['Male', 'Female'])
st.selectbox('Select gender', ['Male', 'Female'])
st.multiselect('Choose planets', ['Jupiter', 'Mars', 'Neptune'])
st.select_slider('Rate it', ['Bad', 'Good', 'Excellent'])
st.slider('Pick a number', 0, 50)

# Input widgets
st.number_input('Enter a number', 0, 10)
st.text_input('Email address')
st.date_input('Travel date')
st.time_input('School time')
st.text_area('Description')
st.file_uploader('Upload a photo')
st.color_picker('Favorite color')

import streamlit as st
import pandas as pd
import numpy as np

#chart visualization
# Create some dummy data
df = pd.DataFrame(np.random.randn(10, 2), columns=['x', 'y'])

st.line_chart(df) # [cite: 56, 57]
st.bar_chart(df)  # [cite: 57, 58]
st.area_chart(df) # [cite: 58, 59]

# Map visualization (requires lat/lon columns) [cite: 62, 63]
map_df = pd.DataFrame(
    np.random.randn(500, 2) / [50, 50] + [51.5080, -0.1281],
    columns=['lat', 'lon']
)
st.map(map_df) # [cite: 64]

# Displays the string "x = 2021" as a code block
st.code("x = 2021")
st.balloons()
st.snow()
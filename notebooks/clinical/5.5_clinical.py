import streamlit as st

st.set_page_config(layout="wide")
st.title("Fusion Tools Integration")

# Embed Fusion Tools page
st.subheader("Fusion Visualization")
st.components.v1.iframe(
    "https://fusion.hubmapconsortium.org/Visualization",
    height=800,
    scrolling=True
)

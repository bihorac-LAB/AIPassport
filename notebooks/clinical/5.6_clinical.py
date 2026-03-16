import streamlit as st
import streamlit.components.v1 as components

st.title("5.6 Consistency in Biomedical Image Analysis (Clinical)")

# header_cols = st.columns(3)
# with header_cols[1]:
#     st.image("module_1_fundamentals/resources/1.1_header.png", width=300)


with open("reference/raw-notebook-files/5.6 jupyter clinical.html", "r") as f:
    html_string = f.read()

components.html(html_string, height=800, scrolling=True)

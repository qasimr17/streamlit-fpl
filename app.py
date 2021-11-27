import os 
import streamlit as st 


# Custom Imports 
from multipage import Multipage 
from pages import overall, your_performance # import all pages 

# Create instance of app 
app = Multipage()

app.add_page("Overall Data", overall.app)
app.add_page("My Performance", your_performance.app)


# Main application
app.run()
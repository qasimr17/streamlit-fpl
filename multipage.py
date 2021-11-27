"""
This file contains the framework for generating the multi page Streamlit FPL application
through an OOP structure.
"""
import streamlit as st 

class Multipage:

	""" Framework for combining multiple streamlit applications."""
	def __init__(self) -> None:
		self.pages = []

	def add_page(self, title, func) -> None:

		self.pages.append({
			"title": title,
			"func":func
			})


	def run(self) -> None:
		page = st.sidebar.selectbox(
    		'App Naviagaton',
    		self.pages,
    		format_func=lambda page: page['title'])

		page['func']()
import time
import json
import requests
import pandas as pd 
import numpy as np
import streamlit as st 
import plotly.express as px 
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def get_base_data():

	url = 'https://fantasy.premierleague.com/api/bootstrap-static/'

	response = ''
	while response == '':
		try:
			response = requests.get(url)
		except:
			time.sleep(5)

	if response.status_code != 200:
		raise Exception(f"Response was code {response.status_code}")

	data = json.loads(response.text)

	return data 



def clean_base_data(dataframe):

	# Keep only the gamweek number, average points and highest points columns
	df_subset = dataframe[['id', 'average_entry_score', 'highest_score']]

	# Keep entries of only completed gameweek
	df_subset = df_subset[~df_subset['highest_score'].isna()]
	df_subset = df_subset.astype('int64')
	df_subset.rename(columns={'id': 'gameweek', 'average_entry_score':'average_score'}, inplace=True)
	# df_subset.set_index('id', inplace=True)


	return df_subset


@st.cache
def create_lookup(base_data):

	elements = pd.DataFrame(base_data['elements'])
	lookup_table = elements[['id', 'web_name', 'event_points']]

	return lookup_table






## Plots and Visualisations

def create_overall_plots():

	fig = go.Figure(data=go.Table(header=dict(values=list(df_subset.columns.str.upper())),
		cells=dict(values=[df_subset.gameweek,df_subset.average_score, df_subset.highest_score])),
	layout=layout)

		# plt = px.line(df_melt, x='gameweek', y='value', color='color')

	plt = px.line(df_subset, x='gameweek', y=['average_score','highest_score'],
		labels={
			"gameweek": "Gameweek",
			"value": "Points",
			"variable": "Type"
		},
		title = "Average and Highest points across each gameweek")
		
	plt.update_layout(margin=dict(l=0,r=0,t=30,b=100))
	st.write(fig)
	st.write(plt)	

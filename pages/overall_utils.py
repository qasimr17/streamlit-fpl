import time
import json
import requests
import pandas as pd 
import numpy as np
import streamlit as st 
import plotly.express as px 
import plotly.graph_objects as go
from plotly.subplots import make_subplots

@st.cache
def get_base_data():

	""" Returns data from base fpl api. """

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



def clean_base_events_data(dataframe):

	""" Returns a cleaned events dataframe keeping only average and highest score columns for all 
	completed gameweeks."""

	# Keep only the gamweek number, average points and highest points columns
	df_subset = dataframe[['id', 'average_entry_score', 'highest_score']]

	# Keep entries of only completed gameweek
	df_subset = df_subset[~df_subset['highest_score'].isna()]
	df_subset = df_subset.astype('int64')
	df_subset.rename(columns={'id': 'gameweek', 'average_entry_score':'average_score'}, inplace=True)


	return df_subset

def create_lookup(base_data):

	elements = pd.DataFrame(base_data['elements'])
	lookup_table = elements[['id', 'web_name', 'event_points']]

	return lookup_table


def create_overall_visuals(df_subset):

	" Returns plotly charts for showing overall graphics. "

	layout = go.Layout(
  	margin=go.layout.Margin(
        l=0, #left margin
        r=0, #right margin
        b=0, #bottom margin
        t=50  #top margin
    	)
	)

	fig = go.Figure(data=go.Table(header=dict(values=list(df_subset.columns.str.upper())),
		cells=dict(values=[df_subset.gameweek,df_subset.average_score, df_subset.highest_score])),
	layout=layout)

	plt = px.line(df_subset, x='gameweek', y=['average_score','highest_score'],
		labels={
			"gameweek": "Gameweek",
			"value": "Points",
			"variable": "Type"
		},
		title = "Average and Highest points across each gameweek")
		
	plt.update_layout(margin=dict(l=0,r=0,t=30,b=100))

	return fig, plt


def top_performing_players(lookup_table, events):

	""" Returns data frame containing name and points of top performing player of each gameweek."""
	
	top_players_list = list()

	# check completed events only
	events_filtered = events[~events['highest_score'].isna()]
	# get id of top performing player of each gameweek played
	top_elements = events_filtered['top_element'].astype(int)	

	for index, top in enumerate(top_elements):
		player = lookup_table.loc[lookup_table.id == top, "web_name"].item()
		points = events_filtered['top_element_info'][index]['points']
		top_players_list.append(dict(gameweek=index+1, player=player, points=points))

	return top_players_list


def create_bubble_chart_df(elements):

	""" Returns data frame of players who have played at least 180 minutes and have scored at least a point,
	with their cost and points per million information. """

	bubble_chart_df = elements[['id', 'web_name', 'element_type', 'total_points', 'now_cost', 'points_per_game', 'minutes']]
	bubble_chart_df['now_cost'] =  bubble_chart_df['now_cost'] / 10
	bubble_chart_df['points_per_million'] = round(bubble_chart_df['total_points'] / bubble_chart_df['now_cost'], 2)
	bubble_chart_df = bubble_chart_df.query("total_points > 0 and minutes > 180")

	return bubble_chart_df
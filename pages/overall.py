import time
import json
import requests
import numpy as np
import pandas as pd 
import streamlit as st 
import plotly.express as px 
from pages import overall_utils
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def app():

	layout = go.Layout(
  	margin=go.layout.Margin(
        l=0, #left margin
        r=0, #right margin
        b=0, #bottom margin
        t=50  #top margin
    	)
	)

	base_data = overall_utils.get_base_data()
	events = pd.DataFrame(base_data['events'])

	## header = st.container()
	## interactive_container = st.container()


	## with header:
	st.title("Welcome to my Fantasy Premier League Data Visualisation App")
	st.text("View the most important visuals in the fantasy premier league app.")


	df_subset = overall_utils.clean_base_data(events)

	## with interactive_container:

	st.header("An overview of the season so far")
	st.text("Figures below provide a summary of the average and top performing players' \nsummary over the course of this season.")


	## overall_utils.create_overall_plots(df_subset)

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
	st.write(fig)
	st.write(plt)	



# Now creating plots for top performing players
	lookup_table = overall_utils.create_lookup(base_data)
	top_players_list = list()

	# check completed events only
	events_filtered = events[~events['highest_score'].isna()]
	# get id of top performing player of each gameweek played
	top_elements = events_filtered['top_element'].astype(int)	

	for index, top in enumerate(top_elements):
		player = lookup_table.loc[lookup_table.id == top, "web_name"].item()
		points = events_filtered['top_element_info'][index]['points']
		top_players_list.append(dict(gameweek=index+1, player=player, points=points))

	elements = pd.DataFrame(base_data['elements'])
	# Creating bubble chart
	check = elements[['id', 'web_name', 'element_type', 'total_points', 'now_cost', 'points_per_game', 'minutes']]
	check['now_cost'] =  check['now_cost'] / 10
	check['points_per_million'] = round(check['total_points'] / check['now_cost'], 2)
	check = check.query("total_points > 0 and minutes > 180")

	st.header("Top Performing Players")
	top_players_df = pd.DataFrame(top_players_list)
	# st.write(top_players_df)

	fig = px.bar(top_players_df, x = 'points', y = 'gameweek', text='player',
		orientation='h',
		title="Top performing players each gameweek (by points)",
		width = 800)

	fig.update_traces(textposition='outside')
	fig.update_layout(margin=dict(l=0,r=0,t=35,b=100))

	st.write(fig)

	pos_list = ['Goalkeeper', 'Defender', 'Midfielder', 'Forward']
	position = st.selectbox('Select Player Position:', pos_list)

	if position == "Forward":
		fig2 = px.scatter(check.query("element_type==4"), x = 'now_cost', y = 'total_points',
            size = 'points_per_million', color = 'web_name')
		st.write(fig2)

	elif position == "Midfielder":
		fig2 = px.scatter(check.query("element_type==3"), x = 'now_cost', y = 'total_points',
            size = 'points_per_million', color = 'web_name')
		st.write(fig2)

	elif position == "Defender":
		fig2 = px.scatter(check.query("element_type==2"), x = 'now_cost', y = 'total_points',
            size = 'points_per_million', color = 'web_name')
		st.write(fig2)

	elif position == "Goalkeeper":
		fig2 = px.scatter(check.query("element_type==1"), x = 'now_cost', y = 'total_points',
            size = 'points_per_million', color = 'web_name')
		st.write(fig2)
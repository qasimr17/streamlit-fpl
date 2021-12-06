import time
import json
import requests
import numpy as np
import pandas as pd
from requests.api import head 
import streamlit as st 
import plotly.express as px 
from pages import my_performance_utils, overall_utils
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def highlight(row):

	""" Highlights row of data frame if row contains captain's info. """

	if row.is_captain == True:
		return ['background-color: orange'] * 6
	else:
		return ['background-color: white'] * 6

def app():

	# Get basic information and tables:
	base_data = overall_utils.get_base_data()
	events = pd.DataFrame(base_data['events'])
	elements = pd.DataFrame(base_data['elements'])
	lookup_table = elements[['id', 'web_name']]

	header = st.container()
	with header:
		header.title("View your performance over the season")
		fpl_id = header.text_input("Enter Your FPL ID", value = 132645)

		manager_info = my_performance_utils.manager_info(fpl_id)
		header.write(f"Welcome, {manager_info['player_first_name']} {manager_info['player_last_name']}.")
		header.write(f"You are currently ranked {manager_info['summary_overall_rank']} in the world.")
		header.write("Here is a table depicting your performance in all of your leagues:")
		# create dataframe containing manager's rankings in all of the leagues
		classic_leagues = pd.DataFrame(manager_info['leagues']['classic'])[['name', 'entry_rank', 'entry_last_rank']]
		header.dataframe(classic_leagues)
		header.write("\n")

	# Create table showing performance in each gameweek played so far
	current_performance = st.container()
	with current_performance:
		manager_data = my_performance_utils.current_data(fpl_id)
		current_data_df = pd.DataFrame(manager_data['current'])

		# cleaning up the data frame:
		current_data_df['bank'] = current_data_df['bank'] / 10
		current_data_df['value'] = current_data_df['value'] / 10
		current_data_df['points_after_hits'] = current_data_df['points'] - current_data_df['event_transfers_cost']

		current_performance.header('Get a sense of your season so far:')
		current_performance.dataframe(current_data_df)
		current_performance.write("\n")


	visualising_performance = st.container()
	with visualising_performance:
		visualising_performance.header('Visualizing your performance:')

		# Getting overall average data


		df_subset = overall_utils.clean_base_events_data(events)


		current_data_df['average_points'] = df_subset.average_score

		# create line plot showing points, points_after_hits and average points across the season
		plt = px.line(current_data_df, x='event', y=['points','points_after_hits','average_points'],
			labels={
				"event": "Gameweek",
				"_value": "Points",
				"variable": "Type"
			},
			title = "Points across each gameweek")

		# create line plot showing rank across the season
		plt_rank = px.line(current_data_df, x = 'event', y = ['overall_rank'],
			labels = {
			"event": "Gameweek",
			"_value": "Rank",
			"variable": "Type"
			},
			title="Your Overall Rank")

		visualising_performance.plotly_chart(plt)
		visualising_performance.plotly_chart(plt_rank)
		visualising_performance.write("\n")

# Captaincy and Top Performing Players	
	gameweek_data = st.container()
	with gameweek_data:	
		gameweek_data.header("Gameweek by Gameweek Performance")
		gameweek_data.text("View the team you selected each gameweek.")

		gw_data = my_performance_utils.gameweek_data(fpl_id)
		lookup_table = elements[['id', 'web_name']]
		CURRENT_GW = len(gw_data)

		gameweek_id = gameweek_data.number_input("Enter Gameweek ID you want to check", min_value=1, max_value= CURRENT_GW, value = 1)

		# get a manager's 15-man team for each gameweek
		gw_data_df = pd.DataFrame(gw_data[gameweek_id]['picks'])
		# get correct web_name of player against their ID
		gw_data_df['player'] = np.array([lookup_table.loc[lookup_table.id == id, "web_name"] for id in gw_data_df['element']])


		di_gw_data= my_performance_utils.create_display_gw_data(gw_data_df, gameweek_id)

		gameweek_data.text("Table is sorted based on the raw points each player gained.")
		gameweek_data.text("Row in Orange highlights your captain's performance in the week.")
		gameweek_data.text("Multipler = 0 means the player was on your bench while Multipler = 2 means\nthe player was your captain.")
		gameweek_data.dataframe(di_gw_data.style.apply(highlight, axis=1))
		gameweek_data.write("\n")



	# Captaincy:
	captain_performances = st.container()
	with captain_performances:
		captain_performances.header("Your Captains' Performances")
		caps_df, cap_fig = my_performance_utils.captain_performances(gameweek_data=gw_data, lookup_table=lookup_table, current_gw=CURRENT_GW)

		# display horizontal bar chart displaying points gained by captain each gameweek
		captain_performances.plotly_chart(cap_fig)

		captain_performances.write("\n")
		captain_performances.write("Compare your weekly captain choices with the top scoring player in your team")
		best_players = my_performance_utils.combined_df(gw_data, CURRENT_GW, lookup_table)
		caps_df = caps_df[['gameweek', 'captain', 'points']]
		df = pd.concat([caps_df, best_players], axis=1, join="inner")

		# display data frame showing captain and top players performances for each gameweek
		captain_performances.dataframe(df)

		fig = go.Figure()

		fig.add_trace(go.Bar(x=caps_df.gameweek,
							y=df.points,
							name='Captain',
							marker_color='rgb(55, 83, 109)'))

		fig.add_trace(go.Bar(x=caps_df.gameweek,
							y=df.score,
							name='Top Player',
							marker_color='rgb(26, 118, 255)'))

		fig.update_layout(
		title='Your Captain and Top Performers',
		xaxis_tickfont_size=14,
		yaxis=dict(
			title='Points',
			titlefont_size=16,
			tickfont_size=14,
		),
		legend=dict(
			x=0,
			y=1.0,
			bgcolor='rgba(255, 255, 255, 0)',
			bordercolor='rgba(255, 255, 255, 0)'
		),
		barmode='group',
		bargap=0.15, # gap between bars of adjacent location coordinates.
		bargroupgap=0.1 # gap between bars of the same location coordinate.
	)

		# display combined barplot comparing captain and top player performance for each gameweek
		captain_performances.plotly_chart(fig)





	

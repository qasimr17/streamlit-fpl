import time
import json
import requests
import numpy as np
import pandas as pd 
import streamlit as st 
import plotly.express as px 
from pages import my_performance_utils, overall_utils
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def app():

	# # header = st.container()
	st.title("View your performance over the season")
	fpl_id = st.text_input("Enter Your FPL ID", value = 3417811)
	# # st.write(fpl_id)
	manager_info = my_performance_utils.manager_info(fpl_id)
	# # st.text(fpl_id)
	st.write(f"Welcome, {manager_info['player_first_name']} {manager_info['player_last_name']}.")
	# pass

	manager_data = my_performance_utils.current_data(fpl_id)
	current_data_df = pd.DataFrame(manager_data['current'])

	# cleaning up the data frame:
	current_data_df['bank'] = current_data_df['bank'] / 10
	current_data_df['value'] = current_data_df['value'] / 10
	current_data_df['points_after_hits'] = current_data_df['points'] - current_data_df['event_transfers_cost']

	st.header('Get a sense of your season so far:')
	st.dataframe(current_data_df)

	st.write("\n")
	st.header('Visualizing your performance:')

	## Getting overall average data
	base_data = overall_utils.get_base_data()
	events = pd.DataFrame(base_data['events'])
	elements = pd.DataFrame(base_data['elements'])
	df_subset = overall_utils.clean_base_data(events)
	current_data_df['average_points'] = df_subset.average_score

	plt = px.line(current_data_df, x='event', y=['points','points_after_hits','average_points'],
		labels={
			"event": "Gameweek",
			"_value": "Points",
			"variable": "Type"
		},
		title = "Points across each gameweek")

	st.plotly_chart(plt)


	plt_rank = px.line(current_data_df, x = 'event', y = ['overall_rank'],
		labels = {
		"event": "Gameweek",
		"_value": "Rank",
		"variable": "Type"
		},
		title="Your Overall Rank")

	st.plotly_chart(plt_rank)

	# Captaincy and Top Performing Players
	st.write("\n")
	st.header("Gameweek by Gameweek Performance")
	st.text("View the team you selected each gameweek.")

	# get gameweek by gameweek data:
	gw_data = my_performance_utils.gameweek_data(fpl_id)
	# create lookup table to get names from ids
	lookup_table = overall_utils.create_lookup(base_data)
	CURRENT_GW = len(gw_data)
	gameweek_id = st.number_input("Enter Gameweek ID you want to check", min_value=1, max_value= CURRENT_GW, value = 1)

	gw_data_df = pd.DataFrame(gw_data[gameweek_id]['picks'])
	gw_data_df['player'] = np.array([lookup_table.loc[lookup_table.id == id, "web_name"] for id in gw_data_df['element']])


	di_gw_data= my_performance_utils.create_display_gw_data(gw_data_df, gameweek_id)
	# di_gw_data = gw_data_df[['player', 'multiplier', 'is_captain', 'is_vice_captain']]


	# # ## attach gameweek points to dataframe as well
	# di_gw_data['points'] = my_performance_utils.get_player_points_gw(gw_data_df['element'], gameweek_id-1)
	# di_gw_data['effective_points'] = di_gw_data['points'] * di_gw_data['multiplier']
	def highlight(row):

		if row.is_captain == True:
			return ['background-color: orange'] * 6
		else:
			return ['background-color: white'] * 6

	st.text("Table is sorted based on the raw points each player gained.")
	st.text("Row in Orange highlights your captain's performance in the week.")
	st.text("Multipler = 0 means the player was on your bench while Multipler = 2 means\nthe player was your captain.")
	st.dataframe(di_gw_data.style.apply(highlight, axis=1))



	# Captaincy:
	st.write("\n")
	st.header("Your Captains' Performances")


	cap_dict = dict()
	for i in range(CURRENT_GW):
	    for element in gw_data[i+1]['picks']:
	        if element['is_captain'] == True:
	            cap_dict[i] = element['element']
	            break

	cap_names = [lookup_table.loc[lookup_table.id == id, "web_name"].item() for id in cap_dict.values()]

	cap_points = list()
	for k, v in cap_dict.items():
	    cap_points.append(my_performance_utils.get_player_points(v, k))

	caps_df = pd.DataFrame(dict(captain=cap_names, points=cap_points))
	caps_df['gameweek'] = caps_df.index + 1

	cap_fig  = px.bar(caps_df, x = 'points', y = 'gameweek', text='captain',
		orientation='h',
		title="Points scored by your captains",
		width = 800)

	cap_fig.update_traces(textposition='outside')
	st.plotly_chart(cap_fig)
	# # get 
	# cap_data = my_performance_utils.captaincy_data(fpl_id)

	# cap_list = my_performance_utils.get_captain_list(cap_data)
	# # st.dataframe(cap_list)

	# lookup_table = overall_utils.create_lookup(base_data)
	# cap_names = np.array([lookup_table.loc[lookup_table.id == id, "web_name"] for id in cap_list])

	# st.dataframe(cap_names)

	# Combined df
	# gw_top_players = list()
	# for i in range(CURRENT_GW):
	#     gw_scores = list()
	#     for element in gw_data[i+1]['picks']:
	#         gw_scores.append(dict(player_id = element['element'], score = my_performance_utils.get_player_points(element['element'], i)))
	#     highest_score = max(gw_scores, key = lambda x: x['score'])                        
	#     gw_top_players.append(highest_score)

	# best_players = pd.DataFrame(gw_top_players)
	# best_players['top_player'] = [lookup_table.loc[lookup_table.id == id, "web_name"].item() for id in best_players.player_id]
	# best_players = best_players[['top_player', 'score']]
	st.write("\n")
	st.write("Compare your weekly captain choices with the top scoring player in your team")
	best_players = my_performance_utils.combined_df(gw_data, CURRENT_GW, lookup_table)
	caps_df = caps_df[['gameweek', 'captain', 'points']]
	df = pd.concat([caps_df, best_players], axis=1, join="inner")
	st.dataframe(df)

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

	st.plotly_chart(fig)





	
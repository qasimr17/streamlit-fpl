import pandas as pd 
import streamlit as st 
import plotly.express as px 
from pages import overall_utils


def app():

	# get base information that has further events, elements etc data 
	base_data = overall_utils.get_base_data()
	events = pd.DataFrame(base_data['events'])
	elements = pd.DataFrame(base_data['elements'])


	# create a header container for displaying main text
	header = st.container()
	with header:
		header.title("Welcome to my Fantasy Premier League Data Visualisation App")
		header.text("View the most important visuals in the fantasy premier league app.")

	# cleaned events data with gameweek, average and highest scores
	df_subset = overall_utils.clean_base_events_data(events)

	# creating overall performance table and plot
	overall_visual = st.container()
	with overall_visual:
		overall_visual.header("An overview of the season so far")
		overall_visual.text("Figures below provide a summary of the average and top performing players' \nsummary over the course of this season.")

		table, plot = overall_utils.create_overall_visuals(df_subset=df_subset)
		overall_visual.plotly_chart(table)
		overall_visual.plotly_chart(plot)	

	

	top_performers = st.container()
	lookup_table = elements[['id', 'web_name']]
	# get data frame containing names and points of each gameweek's top players
	top_players_list = overall_utils.top_performing_players(lookup_table=lookup_table, events=events)

	# create bubble chart to show points per value of all players 
	bubble_chart_df = overall_utils.create_bubble_chart_df(elements=elements)

	with top_performers:
		top_performers.header("Top Performing Players")
		top_players_df = pd.DataFrame(top_players_list)

		fig = px.bar(top_players_df, x = 'points', y = 'gameweek', text='player',
			orientation='h',
			title="Top performing players each gameweek (by points)",
			width = 800)

		fig.update_traces(textposition='outside')
		fig.update_layout(margin=dict(l=0,r=0,t=35,b=100))

		# display horizontal bar chart of top performing players of each gameweek
		st.plotly_chart(fig)

		# preparing data for bubble chart
		pos_list = ['Goalkeeper', 'Defender', 'Midfielder', 'Forward']
		position = st.selectbox('Select Player Position:', pos_list)

		if position == "Forward":
			fig2 = px.scatter(bubble_chart_df.query("element_type==4"), x = 'now_cost', y = 'total_points',
				size = 'points_per_million', color = 'web_name')
			st.write(fig2)

		elif position == "Midfielder":
			fig2 = px.scatter(bubble_chart_df.query("element_type==3"), x = 'now_cost', y = 'total_points',
				size = 'points_per_million', color = 'web_name')
			st.write(fig2)

		elif position == "Defender":
			fig2 = px.scatter(bubble_chart_df.query("element_type==2"), x = 'now_cost', y = 'total_points',
				size = 'points_per_million', color = 'web_name')
			st.write(fig2)

		elif position == "Goalkeeper":
			fig2 = px.scatter(bubble_chart_df.query("element_type==1"), x = 'now_cost', y = 'total_points',
				size = 'points_per_million', color = 'web_name')
			st.write(fig2)
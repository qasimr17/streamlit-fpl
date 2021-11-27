import time
import json
import requests
import pandas as pd 
import numpy as np
import streamlit as st 
from itertools import repeat
# import plotly.express as px 
# import plotly.graph_objects as go
# from plotly.subplots import make_subplots


def manager_info(id):

	base_url = 'https://fantasy.premierleague.com/api/entry/'
	id_url = base_url + str(id) + '/'

	response = ''
	while response == '':
		try:
			response = requests.get(id_url)
		except:
			time.sleep(5)
	if response.status_code != 200:
		if response.status_code == 503:
			raise Exception(f"The game is currently updating, please try again at a later time.")
		else:
			raise Exception(f"Response was code {response.status_code}. Please Enter a valid FPL ID.")

	data = json.loads(response.text)

	return data 

@st.cache
def current_data(id):

	base_url = "https://fantasy.premierleague.com/api/entry/"
	full_url = base_url + str(id) + '/history/'

	response = ''
	while response == '':
		try:
			response = requests.get(full_url)
		except:
			time.sleep(5)
	if response.status_code != 200:
		raise Exception(f"Response was code {response.status_code}.")

	data = json.loads(response.text)

	return data 

@st.cache
def gameweek_data(id):

	base_url = f"https://fantasy.premierleague.com/api/entry/{id}/event/"
	events_dict = dict()

	for event in range(1, 39):
		response = ''
		full_url = base_url + str(event) + '/picks/'
		while response == '':
			try:
				response = requests.get(full_url)

			except:
				time.sleep(5)

		if response.status_code != 200:
			break

		data = json.loads(response.text)
		events_dict[event] = data

	return events_dict


def get_captain_list(cap_data):

	cap_list = list()
	for k, v in cap_data.items():
		for element in v['picks']:
			if element['is_captain'] == True:
				cap_list.append(element['element'])

	return np.array(cap_list)

@st.cache
def get_player_points(player_id, gameweek):
    
    url = f"https://fantasy.premierleague.com/api/element-summary/{player_id}/"
    response = ''
    while response == '':
        try:
            response = requests.get(url)
        except:
            time.sleep(5)

    if response.status_code != 200:
        raise Exception(f"Response was code {response.status_code}")
    
    data = json.loads(response.text)

    try:
    	points = data['history'][gameweek]['total_points']
    except:
    	points = np.nan
    
    return points


def get_player_points_gw(list_of_players, gameweek):

	return np.array(map(get_player_points, list_of_players, repeat(gameweek)))

@st.cache
def create_display_gw_data(generic_gw_data, gameweek_id):
	di_gw_data = None

	di_gw_data = generic_gw_data[['player', 'multiplier', 'is_captain', 'is_vice_captain']]

	## attach gameweek points to dataframe as well
	di_gw_data['points'] = get_player_points_gw(generic_gw_data['element'], gameweek_id-1)
	di_gw_data['effective_points'] = di_gw_data['points'] * di_gw_data['multiplier']
		
	return di_gw_data.sort_values(by=['points', 'effective_points'], ascending=False)


def top_player_chart(generic_gw_data, current_gw):

	for i in range(current_gw):
		data = create_display_gw_data(generic_gw_data, i)
		top_player, points, is_captain = data[0][['player', 'points', 'is_captain']]

@st.cache
def combined_df(gw_data, current_gw, lookup_table):

	gw_top_players = list()
	for i in range(current_gw):
	    gw_scores = list()
	    for element in gw_data[i+1]['picks']:
	        gw_scores.append(dict(player_id = element['element'], score = get_player_points(element['element'], i)))
	    highest_score = max(gw_scores, key = lambda x: x['score'])                        
	    gw_top_players.append(highest_score)

	best_players = pd.DataFrame(gw_top_players)
	best_players['top_player'] = [lookup_table.loc[lookup_table.id == id, "web_name"].item() for id in best_players.player_id]
	best_players = best_players[['top_player', 'score']]

	return best_players

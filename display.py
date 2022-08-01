#!/usr/bin/env python
# coding: utf-8



import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from datetime import date, timedelta



# Loads the CSV of the selected date
def get_df_from_date(pick_date):
  date_str = '-'.join([str(pick_date.year), str(pick_date.month), str(pick_date.day)])
  filename = date_str + '.csv'
  url = 'https://storage.googleapis.com/the-filthiest/pitch-data/' + filename
  return pd.read_csv(url, index_col = 0)

# Displays KDE plot for selected pitch
def kdeplot(graph_sort, graph_sort_in, leader, df_all, pitch_type, pitch_type_in):
  fig = plt.figure(figsize = (12,4))
  sns.set_theme('notebook')
  if pitch_type == '(none)':
    df_filter = df_all
  else:
    df_filter = df_all.loc[df_all['pitch_type'] == pitch_type]
  ax = sns.kdeplot(x = df_filter[graph_sort])
  ax.set_xlabel(graph_sort_in)
  text_y = ax.get_ylim()[1]
  
  # Annotation to display selected pitch
  ax.annotate(f"{leader.pitcher}'s {leader.pitch_type_raw}", xy = (leader[graph_sort], 0), xytext = (leader[graph_sort], text_y/2),
                arrowprops = dict(color = 'red'), horizontalalignment = 'center')
  if pitch_type == '(none)':
    pitch_type_in = 'all pitche'
  ax.set(title = f'Distribution of {graph_sort_in} for {pitch_type_in}s on {pick_date}')
  st.pyplot(fig)

st.write('# The Filthiest ⚾')
  
# Defaults to yesterday, but displays previous day if no game data
pick_date = date.today() + timedelta(days = -1)
try:
  df = get_df_from_date(pick_date)
except:
  pick_date = date.today() + timedelta(days = -2)
  df = get_df_from_date(pick_date)

# Allows user to pick a date between opening day and yesterday
opening_day = date(2022, 4, 7)
pick_date = st.sidebar.date_input(label = 'Pitches from date:', value = pick_date, min_value = opening_day, max_value =pick_date)
df = get_df_from_date(pick_date)
df['vbreak'] = df['vbreak'].apply(round)
df['hbreak'] = df['hbreak'].apply(round)


sort_in_list = ('FiFaX', 'MPH', 'RPM', 'VBreak', 'HBreak')
sort_list = ('fifax', 'mph', 'rpm', 'vbreak', 'hbreak')
pitch_type_list = ('(none)', '4-Seam Fastball', 'Slider', '2-Seam Fastball/Sinker', 'Changeup', 'Curveball', 'Splitter/Knuckleball', 'Cutter')

# User inputs
pitch_type_in = st.sidebar.selectbox('Pitch type:', pitch_type_list)
sort_in = st.sidebar.selectbox('Sort by:', sort_in_list)
pitcher_search = st.sidebar.text_input('Pitcher search:', value = '')
hitter_wins = st.sidebar.checkbox('Show hitter victories instead (#HittingSamurai)')

st.sidebar.write('**The Filthiest** reads in Statcast data from Baseball Savant and calculates the filthiest pitches thrown each day.')
st.sidebar.write("**FiFaX**, or **Filth Factor eXpected**, is the probability a pitch will be a swinging strike, called strike, or foul tip, given that the pitch is a strike or put in play.")
st.sidebar.write('Predictions are given by a Random Forest model trained on all pitches thrown in 2021.')
st.sidebar.write('Created by Dayv Doberne | [Twitter](https://www.twitter.com/Sunyveil_Sports)')
st.sidebar.write('Inspired by [Pitching Ninja](https://twitter.com/PitchingNinja)')


pitch_dict = {'(none)': '(none)',
              '4-Seam Fastball': 'Fastball',
              'Slider': 'Slider',
              '2-Seam Fastball/Sinker': 'Sinker',
              'Changeup': 'Changeup',
              'Curveball': 'Curveball',
              'Splitter/Knuckleball': 'Splitter',
              'Cutter': 'Cutter'}
sort_dict = {}
for key, value in zip(sort_in_list, sort_list):
  sort_dict[key] = value


pitch_type = pitch_dict[pitch_type_in]
sort = sort_dict[sort_in]

if hitter_wins:
  if 'result_raw' in df.columns:
    df = df.loc[(df['result_raw'] == 'In play, no out') | (df['result_raw'] == 'In play, run(s)')]
  else:
    df = df.loc[(df['result'] == 'Contact') & (df['batter_wins'] == True)]
else:
    df = df.loc[df['result'] == 'Strike']

is_ascending = False # In case any leaderboards show the bottom values

# Filter results by pitch type
if pitch_type == '(none)':
  leaderboard = df.sort_values(by = sort, ascending = is_ascending)
else:
  leaderboard = df.loc[(df.pitch_type == pitch_type)].sort_values(by = sort, ascending = is_ascending)
  
# Filter by pitcher
if pitcher_search != '':
    leaderboard = leaderboard.loc[leaderboard['pitcher'].apply(lambda pitcher_name: pitcher_search.lower() in pitcher_name.lower())]
    
# Display leaderboard
if len(leaderboard) > 0:
    show_n = min(len(leaderboard), 5)
    
    leaderboard_show = leaderboard[['pitcher', 'batter', 'mph', 'rpm', 'vbreak', 'hbreak', 'fifax']]
    leaderboard_show.columns = ['Pitcher', 'Batter', 'Velo (mph)', 'RPM', 'VBreak', 'HBreak', 'FiFaX']
    leaderboard_show.index = range(1, len(leaderboard_show) + 1)
    if pitch_type == '(none)':
      st.write(f'The top {str(show_n)} pitches from MLB games on {pick_date}, sorted by {sort_in}.')
    else:
      st.write(f'The top {str(show_n)} {pitch_type_in}s from MLB games on {pick_date}, sorted by {sort_in}.')
    st.dataframe(leaderboard_show.head(show_n).style.format({'Velo (mph)':"{:.4}", 'FiFaX':"{:.3}"}))
    
    # Allow user to select row from leaderboard
    leader_index = st.selectbox('Select row to watch video:', range(1, show_n + 1))
    leader = leaderboard.iloc[leader_index - 1]
    st.write(f"{leader.pitcher}'s {leader['pitch_type_raw'].lower()} to {leader.batter} in inning {str(leader.inning)}, {leader['count'][1]}-{leader['count'][4]} count.")
    
    # If url for video is not in .csv, use iframe to search it on mlb
    show_search = ('url' not in df.columns)
    if show_search or leader.url == 'None':
      if 'bsquery' in df.columns:
        st.components.v1.iframe(leader.bsquery, height = 600)
      else:
        st.components.v1.iframe(f"https://www.mlb.com/video/search?q={leader.pitcher.replace(' ', '+')}+{leader.batter.replace(' ', '+')}+inning+{str(leader.inning)}+{str(leader['count'][1])}+ball+{str(leader['count'][4])}+strike&qt=FREETEXT", height = 600)
   
    else:
      st.video(leader.url)
      
    # KDE plot for each feature
    for key in sort_in_list:
      kdeplot(sort_dict[key], key, leader, df, pitch_type, pitch_type_in)
        
else:
  st.write('Player not found!')




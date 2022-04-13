#!/usr/bin/env python
# coding: utf-8

# In[31]:


import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import requests


# In[32]:

from datetime import date, timedelta

st.write('# The Filthiest ⚾')


# In[ ]:



# In[ ]:

date = date.today() + timedelta(days = -1)
try:
  
  date_str = '-'.join([str(date.year), str(date.month), str(date.day)])
  filename = date_str + '.csv'
  url = 'https://storage.googleapis.com/the-filthiest/pitch-data/' + filename
  contents = requests.get(url).content
  df = pd.read_csv(url, index_col = 0)
  print('URL get try 1')
except:
  date = date.today() + timedelta(days = -2)
  date_str = '-'.join([str(date.year), str(date.month), str(date.day)])
  filename = date_str + '.csv'
  url = 'https://storage.googleapis.com/the-filthiest/pitch-data/' + filename
  contents = requests.get(url).content
  df = pd.read_csv(url, index_col = 0)
  print('URL get try 2')
  

# In[19]:


pitch_type_in = st.sidebar.selectbox('Pitch type:', ('(none)', '4-Seam Fastball', 'Slider', '2-Seam Fastball/Sinker', 'Changeup', 'Curveball', 'Splitter/Knuckleball', 'Cutter'))

sort_in_list = ('FiFaX', 'MPH', 'RPM', 'VBreak', 'HBreak')
sort_list = ('fifax', 'mph', 'rpm', 'vbreak', 'hbreak')

sort_in = st.sidebar.selectbox('Sort by:', sort_in_list)

leader_index = st.sidebar.selectbox('Select index:', (1,2,3,4,5))
pitcher_search = st.sidebar.text_input('Pitcher search:', value = '')
hitter_wins = st.sidebar.checkbox('Show hitter victories instead')


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


# In[20]:



pitch_type = pitch_dict[pitch_type_in]
sort = sort_dict[sort_in]


# In[25]:
def kdeplot(graph_sort, graph_sort_in, leader, leaderboard, pitch_type_in):
  fig = plt.figure(figsize = (12,4))
  sns.set_theme('notebook')
  ax = sns.kdeplot(x = leaderboard[graph_sort])
  ax.set_xlabel(graph_sort_in)
  text_y = ax.get_ylim()[1]
  ax.annotate(f"{leader.pitcher}'s {leader.pitch_type_raw}", xy = (leader[graph_sort], 0), xytext = (leader[graph_sort], text_y/2),
                arrowprops = dict(color = 'red'), horizontalalignment = 'center')
  if pitch_type == '(none)':
    pitch_type_in = 'all pitche'
  ax.set(title = f'Distribution of {graph_sort_in} for {pitch_type_in}s on {date}')
  st.pyplot(fig)


if hitter_wins:
    df = df.loc[(df['result_raw'] == 'In play, no out') | (df['result_raw'] == 'In play, run(s)')]
else:
    df = df.loc[df['result'] == 'Strike']

is_ascending = False
if pitch_type == '(none)':
  leaderboard = df.sort_values(by = sort, ascending = is_ascending)
else:
  leaderboard = df.loc[(df.pitch_type == pitch_type)].sort_values(by = sort, ascending = is_ascending)
if pitcher_search != '':
    leaderboard = leaderboard.loc[leaderboard['pitcher'].apply(lambda pitcher_name: pitcher_search.lower() in pitcher_name.lower())]
if len(leaderboard) > 0:
    show_n = min(len(leaderboard), 5)
    if leader_index <= show_n:
        leader = leaderboard.iloc[leader_index - 1]
    leaderboard_show = leaderboard[['pitcher', 'batter', 'mph', 'rpm', 'vbreak', 'hbreak', 'fifax']]
    leaderboard_show.columns = ['Pitcher', 'Batter', 'Velo (mph)', 'RPM', 'VBreak', 'HBreak', 'FiFaX']
    leaderboard_show.index = range(1, len(leaderboard_show) + 1)
    if pitch_type == '(none)':
      st.write(f'The top {str(show_n)} pitches from MLB games on {date}, sorted by {sort_in}.')
    else:
      st.write(f'The top {str(show_n)} {pitch_type_in}s from MLB games on {date}, sorted by {sort_in}.')
    st.dataframe(leaderboard_show.head(show_n).style.format({'Velo (mph)':"{:.4}", 'FiFaX':"{:.3}"}))
    
    if leader_index <= show_n:
        st.write(f"{leader.pitcher}'s {leader['pitch_type_raw'].lower()} to {leader.batter} in inning {str(leader.inning)}, {leader['count'][1]}-{leader['count'][4]} count.")
        st.components.v1.iframe(f"https://www.mlb.com/video/search?q={leader.pitcher.replace(' ', '+')}+{leader.batter.replace(' ', '+')}+inning+{str(leader.inning)}+{str(leader['count'][1])}+ball+{str(leader['count'][4])}+strike&qt=FREETEXT", height = 600)
        
    for key in sort_in_list:
      kdeplot(sort_dict[key], key, leader, leaderboard, pitch_type_in)
        
    else:
        st.write('Index out of range!')
else:
    st.write('Player not found!')


# In[22]:





# In[ ]:





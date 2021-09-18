import os

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# st.set_page_config(layout='wide')

df = pd.read_json(os.getenv('DATAPATH'),
                  lines=True,
                  convert_dates=['start_date', 'end_date', 'timestamp'])

start_date, end_date, total_volume = df.loc[0,
                                            ['start_date', 'end_date', 'total_volume']]
total_duration = (end_date - start_date).total_seconds()

target_volumes = []
for idx, timestamp in enumerate(df['timestamp']):
    volume = ((timestamp - start_date).total_seconds() / total_duration) * total_volume
    target_volumes.append(volume)

df['target_volume'] = target_volumes

current_volume = round(df.loc[len(df)-1]['current_volume'], 2)
target_volume = round(df.loc[len(df)-1]['target_volume'], 2)

current_duration = (df.loc[len(df)-1]['timestamp'] - start_date).total_seconds()

estimated_volume = round((current_volume / current_duration) * total_duration, 2)

col_one, col_two, col_three = st.columns((1, 1, 1))
with col_one:
    st.metric('Current Volume',
              f'{current_volume}GB',
              f'{current_volume - target_volume:.2f}GB',
              delta_color='inverse')

with col_two:
    st.metric('Estimated Volume',
          f'{estimated_volume}GB',
          f'{estimated_volume - total_volume:.2f}GB',
          delta_color='inverse')

with col_three:
    st.metric('Available Volume',
              f'{total_volume}GB',
              f'{(estimated_volume - total_volume) / total_volume:.2%}',
              delta_color='inverse')



df = df.rename({
    'current_volume': 'Current',
    'target_volume': 'Target',
    'timestamp': 'Timestamp'
}, axis='columns')
fig = px.line(df,
              x='Timestamp',
              y=['Current', 'Target'])
fig.update_layout(
    yaxis_title='Volume [GB]',
    legend_title=None
)

st.plotly_chart(fig)

col_one, col_two = st.columns((1, 1))
with col_one:
    st.metric('Last update',
              f'{df.loc[len(df)-1]["Timestamp"].strftime("%d.%m.%y %H:%M:%S")}')
with col_two:
    st.metric('Period End',
              f'{end_date.strftime("%d.%m.%y")}')

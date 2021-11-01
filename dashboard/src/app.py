import os

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
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

###
freq = st.selectbox('Select Frequency', ['15min', '30min', '1H'])
agg = st.selectbox('Select Aggregation', ['mean', 'median', 'max', 'sum'])
def interpolate(df: pd.DataFrame, freq: str = freq) -> pd.Series:
    '''Calculates current volumes at given frequencies `freq`.'''
    df = df.copy().set_index('timestamp')
    start_ts = pd.Timestamp(df.index[0]).ceil(freq=freq)
    stop_ts = pd.Timestamp(df.index[-1]).ceil(freq=freq)
    anchor_tss = pd.date_range(start_ts, stop_ts, freq=freq)

    for anchor_ts in anchor_tss:
        df.loc[anchor_ts] = [None]*len(df.columns)

    ser_inter = pd.Series(data=df['current_volume'].interpolate(method='time'),
                           index=anchor_tss)

    return ser_inter

ser_inter = interpolate(df)

def plot_histogram(consumptions: pd.Series,
                   agg: str = 'mean') -> go.Figure:
    '''Plots a histogram of consumptions at given timestamps (index).'''
    df_hist = pd.DataFrame({
        'consumptions': consumptions,
        'deltas': consumptions.diff(1).shift(-1)})
    df_hist.dropna()
    df_hist['hour'] = df_hist.index.hour
    df_hist['minute'] = df_hist.index.minute

    df_hist['interval'] = (
        df_hist['hour'].apply(lambda val: f'{val:02}') +
        ':' +
        df_hist['minute'].apply(lambda val: f'{val:02}')
    )

    df_group = df_hist.groupby('interval').agg(
        deltas_agg=pd.NamedAgg('deltas', agg)
    )

    fig = px.histogram(df_group, x=df_group.index, y=df_group['deltas_agg'])
    fig.update_layout(
        yaxis_title=f'{agg.capitalize()} traffic in {freq} [GB]',
        xaxis_title='Time Interval'
    )
    st.plotly_chart(fig)

plot_histogram(ser_inter, agg)

###

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

import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import json
import numpy as np
import plotly.express as px


st.set_page_config(layout='wide', initial_sidebar_state='expanded')
dataset = pd.read_csv("crop_production.csv")

st.markdown('### Raw dataset')
st.write(dataset.head())

st.markdown('### Features:')
st.write(dataset.columns)



time_hist_color = st.selectbox('Choose which question you want to see?', ('Question_1', 'Question_2','Question_3','Question_4 and 5')) 

indian_state = json.load(open("states_india.geojson",'r'))

state_id_map = {}

for feature in indian_state['features']:
    feature['id'] = feature['properties']['state_code']
    state_id_map[feature['properties']['st_nm']] = feature['id']


dataset.columns = map(str.lower, dataset.columns)

highest_production_whole_year = dataset.groupby(['crop_year', 'state_name']).agg(avg_production=('production', 'mean')).reset_index()
lowest_production_per_year = dataset.groupby(['crop_year', 'state_name']).agg(avg_production=('production', 'mean')).reset_index()
highest_production_whole_year = highest_production_whole_year.groupby('crop_year').apply(lambda x: x.nlargest(1, 'avg_production')).reset_index(drop=True)
lowest_prduction_per_year = lowest_production_per_year.groupby('crop_year').apply(lambda x: x.nsmallest(1, 'avg_production')).reset_index(drop=True)


dataset['state_name'] = dataset['state_name'].replace('Andaman and Nicobar','Andaman & Nicobar Island')
dataset['state_name'] = dataset['state_name'].replace('Telangana ','Telangana')
dataset['state_name'] = dataset['state_name'].replace('Arunachal Pradesh','Arunanchal Pradesh')
dataset['state_name'] = dataset['state_name'].replace('Jammu and Kashmir ','Jammu & Kashmir')
dataset['state_name'] = dataset['state_name'].replace('Dadra and Nagar Haveli','Dadara & Nagar Havelli')

highest_production_whole_year["id"] = highest_production_whole_year["state_name"].apply(lambda x: state_id_map[x])


def barchart():  
        st.markdown('### Which state in India has the highest average crop production across all years?') 
        fig = px.bar(highest_production_whole_year, y = "avg_production", x = "crop_year",
            hover_data=["avg_production"], color="state_name", 
            labels={'pop':'production per state'}, height=400)
        
        st.plotly_chart(fig)

def barchart_lowest():  
        st.markdown('### Which state had lowest crop production in each year?') 
        fig = px.bar(lowest_prduction_per_year, y = "avg_production", x = "crop_year",
            hover_data=["avg_production"], color="state_name", 
            labels={'pop':'production per state'}, height=500)
        
        st.plotly_chart(fig)

def combined_chart():
    fig = go.Figure()

# Add highest production data to the plot
    fig.add_trace(go.Bar(
        x=highest_production_whole_year['crop_year'],
        y=highest_production_whole_year['avg_production'],
        text=highest_production_whole_year['state_name'],
        name='Highest Production',
        marker_color='green',
        textposition='auto',
    ))

    # Add lowest production data to the plot
    fig.add_trace(go.Bar(
        x=lowest_prduction_per_year['crop_year'],
        y=lowest_prduction_per_year['avg_production'],
        text=lowest_prduction_per_year['state_name'],
        name='Lowest Production',
        marker_color='red',
        textposition='auto',
    ))

    # Update layout
    fig.update_layout(
        title='Highest and Lowest Crop Production by Year',
        xaxis=dict(title='Year'),
        yaxis=dict(title='Crop Production'),
        barmode='group',
        width = 900,
    )

    st.plotly_chart(fig)

highest_production_per_state = dataset.groupby(['state_name', 'crop'])['production'].max().reset_index()
highest_production_per_state = dataset.groupby('state_name').apply(lambda x: x.loc[x['production'].idxmax()])
highest_production_per_state = highest_production_per_state[['state_name', 'crop', 'production']]
highest_production_per_state = highest_production_per_state.reset_index(drop=True)

highest_production_per_state['state_name'] = highest_production_per_state['state_name'].replace('Andaman and Nicobar Islands','Andaman & Nicobar Island')
highest_production_per_state['state_name'] = highest_production_per_state['state_name'].replace('Telangana ','Telangana')
highest_production_per_state['state_name'] = highest_production_per_state['state_name'].replace('Arunachal Pradesh','Arunanchal Pradesh')
highest_production_per_state['state_name'] = highest_production_per_state['state_name'].replace('Jammu and Kashmir ','Jammu & Kashmir')
highest_production_per_state['state_name'] = highest_production_per_state['state_name'].replace('Dadra and Nagar Haveli','Dadara & Nagar Havelli')

highest_production_per_state["id"] = highest_production_per_state["state_name"].apply(lambda x: state_id_map[x])

def map_chart():
    fig = px.choropleth(
        highest_production_per_state,
        locations="id",
        geojson=indian_state,
        color="production",
        hover_name="state_name",
        hover_data=["crop"],
        title="Highest Crop yeilds in Each state",
    )
    fig.update_geos(fitbounds="locations", visible=False)

    st.plotly_chart(fig)

production_data = dataset.groupby(['crop_year']).agg(avg_production=('production', 'mean'), avg_area=('area', 'mean')).reset_index()

def correlation():
    fig = px.scatter(production_data, x='crop_year', y=['avg_area','avg_production'], title='Area vs Production')

    fig.update_layout(
            xaxis_title='State_name',
            yaxis_title='Value',
            legend_title='Variables',
        )

    st.plotly_chart(fig)

group_data = dataset.groupby('crop')['production'].sum()
sort_group = group_data.sort_values(ascending=False)
top_5_crops = sort_group.index[:5]
total_top_5_prod = sort_group.iloc[:5].sum()

def pie_chart():
    fig = px.bar(x=top_5_crops, y=group_data[top_5_crops], labels={'x': 'Crop', 'y': 'Production'})
    fig.update_layout(title=f'{total_top_5_prod:,}')

    st.plotly_chart(fig)

filtered_df = dataset[dataset['season'] != 'Whole Year ']

def season_production():
    fig = px.pie(filtered_df, values='production', names='season', title='Season vs Production')

    st.plotly_chart(fig)

season_crop_production = filtered_df.groupby(['season', 'crop'])['production'].sum().reset_index()

def season_crop():
    fig = px.bar(season_crop_production, x='season', y='production', color='crop',
             labels={'Season': 'Season', 'Production': 'Production'},
             title='Season vs Crop Production)')
    
    st.plotly_chart(fig)

state_avg_production = dataset.groupby('state_name')['production'].mean().reset_index()

# Sort the states in descending order of average crop production
state_avg_production = state_avg_production.sort_values(by='production', ascending=False)

# Select the top 10 states with the highest average crop production
top_10_states = state_avg_production.head(5)

def states_per_year():
    fig = px.bar(top_10_states, x='state_name', y='production')
    
    st.plotly_chart(fig)
    
production_sum_per_year = dataset.groupby('crop_year')['production'].sum().reset_index()

def production_year_line_chart():
    fig = px.line(production_sum_per_year, x='crop_year', y='production', title='Sum of Production by Year')
    fig.update_layout(xaxis_title='Year', yaxis_title='Production')
    st.plotly_chart(fig)

if time_hist_color == 'Question_1':
    production_year_line_chart()
    c1, c2 = st.columns((4,4))
    with c1:
        barchart()
    with c2:
        st.write(highest_production_whole_year)
    st.markdown('##### As we can see in the chart, kerela is dominating almost every year.')
    st.markdown('### Top 5 States with Highest Average Crop Production')
    states_per_year()
elif time_hist_color == "Question_2":
    combined_chart()
    Which_one = st.selectbox('Choose which order you want to see?', ('Highest', 'Lowest')) 
    if Which_one == 'Highest':
        barchart()
        st.markdown("##### High production rate in Kerala could be due to abundant rainfall and fertile soil.")
    else:
        barchart_lowest()
        st.markdown("##### Till 2010 the state of Chandigrh has one of the lowest production rate. ")
        st.markdown("##### As it is in west region of India, its a dry state.")
        st.markdown("##### Low production rate in Northeast India could be due to its geography as it is difficult to plant crops in high elevation.")
        

elif time_hist_color == "Question_3":
    st.markdown("### Which state has it's own highest produced crops.")
    c1,c2 = st.columns((4,4))
    with c2:
        st.write(highest_production_per_state)
    with c1:
        map_chart()
        st.markdown("#### It suggest which state should be focused more for specific crop production.")
    st.markdown("### Top 5 Crops by Production\nTotal Production")
    c1,c2 = st.columns((4,4))
    with c2:
        st.write(group_data)
    with c1:
        pie_chart()
    st.markdown("### Season vs Production")
    c1,c2 = st.columns((4,4))
    with c2:
        st.write(filtered_df)
    with c1:
        season_production()
        st.markdown("#### It suggest which season is good for overall production of crops.")

    st.markdown("### Season vs Crop")
    c1,c2 = st.columns((4,4))
    with c2:
        st.write(season_crop_production)
    with c1:
        season_crop()
        st.markdown("#### It could suggest which crop is best for the each individiual season.")


else:
    st.markdown("### Crops production for each season")
    season = dataset['season'].unique()
    select_season = st.selectbox('Which Season?', (season)) 

    # Filter dataset for summer season
    summer_data = dataset[dataset['season'] == select_season]

    # Calculate the highest production per state for each crop
    highest_production_per_state = summer_data.groupby(['state_name', 'crop'])['production'].max().reset_index()
    highest_production_per_state = summer_data.groupby('state_name').apply(lambda x: x.loc[x['production'].idxmax()])
    highest_production_per_state = highest_production_per_state[['state_name', 'crop', 'production']]
    highest_production_per_state = highest_production_per_state.reset_index(drop=True)

    # Rename state names for visualization
    highest_production_per_state['state_name'] = highest_production_per_state['state_name'].replace({
        'Andaman and Nicobar Islands': 'Andaman & Nicobar Island',
        'Telangana ': 'Telangana',
        'Arunachal Pradesh': 'Arunanchal Pradesh',
        'Jammu and Kashmir ': 'Jammu & Kashmir',
        'Dadra and Nagar Haveli': 'Dadara & Nagar Havelli'
    })

    highest_production_per_state["id"] = highest_production_per_state["state_name"].apply(lambda x: state_id_map[x])

    # Create choropleth map
    def summer_path():
        fig = px.choropleth(
            highest_production_per_state,
            locations="id",
            geojson=indian_state,
            color="production",
            hover_name="state_name",
            hover_data=["crop"],
        )
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(title=f'Highest Crop Yields in Each State {select_season}')
        st.plotly_chart(fig)



    c1, c2 = st.columns((4,4))
    with c2:
        st.write(highest_production_per_state)
    with c1:
        summer_path()
        st.markdown("#### The figure above suggest which crops can be produced at specific Season for each State.")
     
     



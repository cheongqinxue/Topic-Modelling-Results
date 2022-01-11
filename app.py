import streamlit as st
import streamlit_wordcloud as wordcloud
import json
import pandas as pd
from rapidfuzz import process, fuzz
import plotly.graph_objects as go
st.set_page_config(layout="wide")
import requests

FILE_URL='https://raw.githubusercontent.com/cheongqinxue/Topic-Modelling-Results/main/v1.1-150k/topic_info.json'

@st.cache
def load():
    resp = requests.get(FILE_URL)
    df = pd.DataFrame([json.loads(l) for l in resp.text.splitlines()])
    index_df = pd.DataFrame()
    
    for i in range(len(df)):
        x = df.iloc[i]
        for w in x['keywords']:
            index_df = index_df.append({'keyword':w,'topic':x['Topic'],'idx':i}, ignore_index=True)
        
    return df, index_df

def renderdf(df, container):
    fig = go.Figure(
            data=[
                go.Table(
                    columnwidth=[1,9],
                    header=dict(values=['Topic Number','Representative Title'],
                        fill_color='lightsteelblue',
                        font_color='black',
                        font_size=15,
                        align='left'),
                    cells=dict(values=[df.index, df.representative_title],
                        fill_color='#EEEEEE',
                        font_size=13,
                        align='left')
                )
            ])
    fig.update_layout(
        margin=dict(l=20, r=20, t=5, b=5),height=250)
    container.plotly_chart(fig, use_container_width=True)

def main():
    df_, index_df = load()
    df = df_.copy(deep=True)
    gettopic = st.sidebar.text_input(label='Enter a topic number to view')
    searchword = st.sidebar.text_input(label='Enter a keyword to search')
    if searchword != '':
        res = process.extract(searchword, index_df.keyword.tolist(), scorer=fuzz.WRatio, limit=10)
        _,_,res = zip(*res)
        res = index_df.iloc[list(res),:]['idx'].tolist()
        res = [{'Topic number':int(r),'Sample Title':df.iloc[int(r)].representative_title} for r in res]
        st.sidebar.write(res)

    if gettopic != '' and gettopic.isnumeric():
        gettopic = int(gettopic)
        if gettopic >= len(df):
            st.write(f'{gettopic} is not valid')
        else:
            x = df.iloc[gettopic]
            st.caption('Representative Title')
            st.markdown(f'#### {x.representative_title}')
            words = [{'text':w, 'value':s} for w, s in zip(x['keywords'], x['keyword_scores'])]
            return_obj = wordcloud.visualize(words, per_word_coloring=False, enable_tooltip=False, 
                layout='archimedean', width='50%', font_min=30, font_max=60)
            st.caption('All members of the topic')
            st.dataframe({'Titles':x['all_titles']}, height=500)

    st.caption('All Topics List')
    renderdf(df, st)

if __name__=='__main__':
    main()

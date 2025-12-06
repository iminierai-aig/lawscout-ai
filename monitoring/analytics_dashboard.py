"""
Analytics Dashboard for LawScout AI
Visualizes usage patterns, performance metrics, and query analytics
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from pathlib import Path
from datetime import datetime, timedelta

st.set_page_config(page_title="LawScout Analytics", page_icon="📊", layout="wide")

def load_analytics(filepath='analytics.json'):
    """Load analytics data from file"""
    try:
        if Path(filepath).exists():
            with open(filepath, 'r') as f:
                data = json.load(f)
            return pd.DataFrame(data)
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading analytics: {e}")
        return pd.DataFrame()

def main():
    st.title("📊 LawScout AI Analytics Dashboard")
    st.markdown("---")
    
    # Load data
    df = load_analytics()
    
    if df.empty:
        st.warning("No analytics data available yet. Start using LawScout AI to generate analytics.")
        return
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].dt.date
    
    # ========== OVERVIEW METRICS ==========
    st.header("📈 Overview")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Queries", len(df))
    
    with col2:
        avg_time = df['total_time'].mean()
        st.metric("Avg Response Time", f"{avg_time:.2f}s")
    
    with col3:
        avg_score = df['top_score'].mean()
        st.metric("Avg Relevance", f"{avg_score:.1%}")
    
    with col4:
        avg_results = df['num_results'].mean()
        st.metric("Avg Results", f"{avg_results:.1f}")
    
    with col5:
        unique_queries = df['query'].nunique()
        st.metric("Unique Queries", unique_queries)
    
    st.markdown("---")
    
    # ========== TIME SERIES ANALYSIS ==========
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📅 Queries Over Time")
        queries_by_date = df.groupby('date').size().reset_index(name='count')
        fig = px.line(queries_by_date, x='date', y='count', 
                     title='Daily Query Volume',
                     labels={'date': 'Date', 'count': 'Number of Queries'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("⚡ Performance Trends")
        perf_by_date = df.groupby('date').agg({
            'search_time': 'mean',
            'generation_time': 'mean',
            'total_time': 'mean'
        }).reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=perf_by_date['date'], y=perf_by_date['search_time'],
                                name='Search Time', mode='lines+markers'))
        fig.add_trace(go.Scatter(x=perf_by_date['date'], y=perf_by_date['generation_time'],
                                name='Generation Time', mode='lines+markers'))
        fig.update_layout(title='Average Response Times', 
                         xaxis_title='Date', yaxis_title='Time (seconds)')
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # ========== COLLECTION USAGE ==========
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📚 Collection Usage")
        collection_counts = df['collection'].value_counts()
        fig = px.pie(values=collection_counts.values, names=collection_counts.index,
                    title='Queries by Collection Type')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Relevance Distribution")
        fig = px.histogram(df, x='top_score', nbins=20,
                          title='Distribution of Top Match Scores',
                          labels={'top_score': 'Relevance Score'})
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # ========== TOP QUERIES ==========
    st.subheader("🔥 Most Common Queries")
    top_queries = df['query'].value_counts().head(10)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        fig = px.bar(x=top_queries.values, y=top_queries.index, orientation='h',
                    labels={'x': 'Count', 'y': 'Query'},
                    title='Top 10 Queries')
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.dataframe(top_queries.reset_index().rename(
            columns={'index': 'Query', 'query': 'Count'}
        ), use_container_width=True)
    
    st.markdown("---")
    
    # ========== PERFORMANCE BREAKDOWN ==========
    st.subheader("⏱️ Performance Breakdown")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Avg Search Time", f"{df['search_time'].mean():.3f}s")
        st.metric("Min Search Time", f"{df['search_time'].min():.3f}s")
        st.metric("Max Search Time", f"{df['search_time'].max():.3f}s")
    
    with col2:
        st.metric("Avg Generation Time", f"{df['generation_time'].mean():.3f}s")
        st.metric("Min Generation Time", f"{df['generation_time'].min():.3f}s")
        st.metric("Max Generation Time", f"{df['generation_time'].max():.3f}s")
    
    with col3:
        st.metric("Avg Total Time", f"{df['total_time'].mean():.3f}s")
        st.metric("Min Total Time", f"{df['total_time'].min():.3f}s")
        st.metric("Max Total Time", f"{df['total_time'].max():.3f}s")
    
    st.markdown("---")
    
    # ========== RECENT QUERIES ==========
    st.subheader("🕐 Recent Queries")
    recent_df = df.sort_values('timestamp', ascending=False).head(20)
    
    display_df = recent_df[['timestamp', 'query', 'collection', 'num_results', 
                            'top_score', 'total_time']].copy()
    display_df['top_score'] = display_df['top_score'].apply(lambda x: f"{x:.1%}")
    display_df['total_time'] = display_df['total_time'].apply(lambda x: f"{x:.2f}s")
    display_df = display_df.rename(columns={
        'timestamp': 'Time',
        'query': 'Query',
        'collection': 'Collection',
        'num_results': 'Results',
        'top_score': 'Relevance',
        'total_time': 'Response Time'
    })
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # ========== EXPORT ==========
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Export CSV",
            data=csv,
            file_name=f"lawscout_analytics_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    with col2:
        json_data = df.to_json(orient='records', date_format='iso')
        st.download_button(
            label="📥 Export JSON",
            data=json_data,
            file_name=f"lawscout_analytics_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json"
        )

if __name__ == "__main__":
    main()


import streamlit as st
from supabase import create_client
import pandas as pd
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=5000,limit=None,key="refresh")
url="https://kgojizbibruhdwcqjxqc.supabase.co"
key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtnb2ppemJpYnJ1aGR3Y3FqeHFjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzgwNTA1OTAsImV4cCI6MjA5MzYyNjU5MH0.bWGfsJUvJ6EuiunV-FjDzQKk8AMPnmYz7D52gmyluVY"
supabase=create_client(url,key)
st.set_page_config(page_title="AI CCTV Dashboard",layout="wide")
st.title("AI CCTV Surveillance Dashboard")
response=supabase.table("alerts").select("*").order("created_at",desc=True).execute()
data=response.data
if data:
    df=pd.DataFrame(data)
    df["created_at"]=pd.to_datetime(df["created_at"])
    st.sidebar.header("Filters")
    event_types=st.sidebar.multiselect("Event Type",options=df["event_type"].unique(),default=df["event_type"].unique())
    min_time=df["created_at"].min().to_pydatetime()
    max_time=df["created_at"].max().to_pydatetime()
    start_time,end_time=st.sidebar.slider("Time Range",min_value=min_time,max_value=max_time,value=(min_time,max_time))
    limit=st.sidebar.slider("Records",5,100,20)
    filtered_df=df[(df["event_type"].isin(event_types))&(df["created_at"]>=pd.to_datetime(start_time))&(df["created_at"]<=pd.to_datetime(end_time))].head(limit)
    st.subheader("Filtered Alerts")
    st.dataframe(filtered_df,width='stretch')
    st.subheader("Event Counts")
    col1,col2,col3=st.columns(3)
    col1.metric("Intrusions",filtered_df[filtered_df["event_type"]=="intrusion"].shape[0])
    col2.metric("Crowd",filtered_df[filtered_df["event_type"]=="crowd"].shape[0])
    col3.metric("Fight",filtered_df[filtered_df["event_type"]=="fight"].shape[0])
    st.subheader("Event Distribution")
    st.bar_chart(filtered_df["event_type"].value_counts())
    st.subheader("Recent Alerts")
    recent_df=df[df["created_at"]>(pd.Timestamp.utcnow()-pd.Timedelta(minutes=1))]
    if not recent_df.empty:
        st.dataframe(recent_df,width='stretch')
    else:
        st.write("No recent alerts")
else:
    st.write("No alerts yet")
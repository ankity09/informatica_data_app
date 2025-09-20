import streamlit as st
import os
import json
import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from model_serving_utils import query_endpoint, query_endpoint_stream, endpoint_supports_feedback, submit_feedback

# Page configuration
st.set_page_config(
    page_title="Informatica Data Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Get serving endpoint from environment
SERVING_ENDPOINT = os.getenv('SERVING_ENDPOINT', 'mas-f63d2792-endpoint')

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "endpoint_supports_feedback" not in st.session_state:
    try:
        st.session_state.endpoint_supports_feedback = endpoint_supports_feedback(SERVING_ENDPOINT)
    except:
        st.session_state.endpoint_supports_feedback = False

# Sidebar
with st.sidebar:
    st.title("🔧 Settings")
    st.write(f"**Endpoint:** {SERVING_ENDPOINT}")
    st.write(f"**Feedback Support:** {'✅' if st.session_state.endpoint_supports_feedback else '❌'}")
    
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Main app
st.title("📊 Informatica Data Intelligence Platform")
st.markdown("---")

# Create tabs
tab1, tab2 = st.tabs(["📈 Dashboard", "💬 AI Assistant"])

with tab1:
    st.header("📈 Data Intelligence Dashboard")
    
    # Mock data for dashboard
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Collections",
            value="2,847",
            delta="12%"
        )
    
    with col2:
        st.metric(
            label="Active Customers",
            value="1,234",
            delta="8%"
        )
    
    with col3:
        st.metric(
            label="Monthly Revenue",
            value="$68,000",
            delta="15%"
        )
    
    with col4:
        st.metric(
            label="Efficiency Score",
            value="94.2%",
            delta="3%"
        )
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Collections Trend")
        collections_data = {
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'Collections': [1200, 1350, 1100, 1400, 1600, 1800]
        }
        df_collections = pd.DataFrame(collections_data)
        
        fig_collections = px.line(
            df_collections, 
            x='Month', 
            y='Collections',
            title="Monthly Collections",
            markers=True
        )
        fig_collections.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_collections, use_container_width=True)
    
    with col2:
        st.subheader("💰 Revenue Trend")
        revenue_data = {
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'Revenue': [45000, 52000, 48000, 55000, 62000, 68000]
        }
        df_revenue = pd.DataFrame(revenue_data)
        
        fig_revenue = px.bar(
            df_revenue, 
            x='Month', 
            y='Revenue',
            title="Monthly Revenue",
            color='Revenue',
            color_continuous_scale='Blues'
        )
        fig_revenue.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_revenue, use_container_width=True)
    
    # Additional insights
    st.subheader("🔍 Key Insights")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **Top Performing Categories:**
        - Data Integration: +25%
        - Analytics: +18%
        - Cloud Services: +22%
        """)
    
    with col2:
        st.success("""
        **Customer Satisfaction:**
        - Overall Score: 4.7/5
        - Response Time: 2.3s
        - Resolution Rate: 96%
        """)

with tab2:
    st.header("💬 AI Assistant")
    st.markdown("Ask me anything about your data intelligence platform!")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about your data..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Prepare messages for the model serving endpoint
                    input_messages = [{"role": "user", "content": prompt}]
                    
                    # Query the Databricks model serving endpoint
                    response_messages, request_id = query_endpoint(
                        endpoint_name=SERVING_ENDPOINT,
                        messages=input_messages,
                        max_tokens=2000,
                        return_traces=st.session_state.endpoint_supports_feedback
                    )
                    
                    # Extract the assistant's response
                    assistant_message = ""
                    if isinstance(response_messages, list) and len(response_messages) > 0:
                        assistant_message = response_messages[0].get("content", "")
                    
                    if not assistant_message:
                        assistant_message = "I'm sorry, I couldn't generate a response. Please try again."
                    
                    # Display the response
                    st.markdown(assistant_message)
                    
                    # Add assistant message to chat history
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": assistant_message,
                        "request_id": request_id
                    })
                    
                    # Feedback section
                    if st.session_state.endpoint_supports_feedback and request_id:
                        st.markdown("---")
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("👍", key=f"positive_{len(st.session_state.messages)}"):
                                try:
                                    submit_feedback(SERVING_ENDPOINT, request_id, 1)
                                    st.success("Thank you for your feedback!")
                                except Exception as e:
                                    st.error(f"Failed to submit feedback: {e}")
                        
                        with col2:
                            if st.button("👎", key=f"negative_{len(st.session_state.messages)}"):
                                try:
                                    submit_feedback(SERVING_ENDPOINT, request_id, 0)
                                    st.success("Thank you for your feedback!")
                                except Exception as e:
                                    st.error(f"Failed to submit feedback: {e}")
                
                except Exception as e:
                    error_message = f"I encountered an error: {str(e)}. Please try again."
                    st.error(error_message)
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": error_message
                    })

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>Informatica Data Intelligence Platform | Powered by Databricks</p>
    </div>
    """, 
    unsafe_allow_html=True
)

# Informatica Data Intelligence - Streamlit App

A modern data intelligence platform built with Streamlit and integrated with Databricks Model Serving.

## Features

### 📈 Dashboard Tab
- **Key Metrics**: Total collections, active customers, monthly revenue, efficiency score
- **Interactive Charts**: Collections trend and revenue visualization using Plotly
- **Key Insights**: Performance categories and customer satisfaction metrics

### 💬 AI Assistant Tab
- **Intelligent Chat**: Powered by Databricks Model Serving endpoint
- **Real-time Responses**: Direct integration with your MAS endpoint
- **Feedback System**: Thumbs up/down feedback for model improvement
- **Chat History**: Persistent conversation history

## Architecture

- **Frontend**: Streamlit with Plotly for visualizations
- **Backend**: Direct integration with Databricks Model Serving
- **Model Serving**: Uses `mas-f63d2792-endpoint` for AI responses
- **Deployment**: Databricks Apps

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   - Set `SERVING_ENDPOINT` environment variable
   - Ensure Databricks authentication is configured

3. **Run Locally**:
   ```bash
   streamlit run streamlit_app.py
   ```

4. **Deploy to Databricks Apps**:
   - Push to your repository
   - Deploy using Databricks Apps

## Configuration

The app uses the following environment variables:
- `SERVING_ENDPOINT`: Databricks model serving endpoint (default: mas-f63d2792-endpoint)
- `STREAMLIT_BROWSER_GATHER_USAGE_STATS`: Disabled for privacy

## Model Serving Integration

The app integrates with Databricks Model Serving using the `model_serving_utils.py` module:
- Handles different response formats from multi-agent supervisors
- Manages authentication and error handling
- Supports feedback submission for model improvement

## Dashboard Data

The dashboard currently displays mock data. To connect to real data sources:
1. Replace the mock data in `streamlit_app.py` with real database queries
2. Add data connection logic for your specific data sources
3. Implement real-time data updates if needed

## Troubleshooting

### Common Issues:
1. **Endpoint Connection**: Verify the `SERVING_ENDPOINT` is correct and accessible
2. **Authentication**: Ensure Databricks authentication is properly configured
3. **Response Format**: Check that the endpoint returns the expected response format

### Debug Mode:
The app includes detailed logging for troubleshooting endpoint connectivity issues.

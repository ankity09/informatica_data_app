# Informatica Data Intelligence App

A modern web application for Informatica that provides a chatbot interface backed by Databricks Model Serving, along with a dashboard for data insights.

## Features

- **🤖 AI Chatbot**: Interactive chat interface powered by Databricks Model Serving
- **📊 Dashboard**: Analytics dashboard with key metrics and embeddable content
- **🎨 Modern UI**: Clean, responsive design built with React and Tailwind CSS
- **⚡ Fast API**: FastAPI backend for efficient API communication
- **🔗 Databricks Integration**: Seamless connection to Databricks Model Serving endpoints

## Architecture

This app follows the Databricks Node.js + FastAPI template structure:

- **Frontend**: React.js with TypeScript, Vite, Tailwind CSS, and Lucide React icons
- **Backend**: FastAPI with Databricks SDK integration
- **Model Serving**: Connects to your Databricks Model Serving endpoint
- **Deployment**: Ready for Databricks Apps deployment

## Prerequisites

- Node.js 18+ and npm
- Python 3.8+
- Databricks workspace with Model Serving endpoint
- Databricks CLI configured

## Setup Instructions

### 1. Install Dependencies

```bash
# Install Node.js dependencies
npm install

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

The app is configured to use the Databricks serving endpoint `agents_ankit_yadav-dbdemos-system_consumption_agent`. For local development, you can set it manually:

```bash
export SERVING_ENDPOINT=agents_ankit_yadav-dbdemos-system_consumption_agent
```

**Note**: Make sure you have Databricks CLI configured for local development:
```bash
databricks configure --token
```

### 3. Build the Frontend

```bash
# Build for production
npm run build

# Or run in development mode
npm run dev
```

### 4. Run the Backend

```bash
# Start the FastAPI server
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Development Mode

For development, you can run both frontend and backend:

```bash
# Terminal 1: Start FastAPI backend
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Start React development server
npm run dev
```

The frontend will be available at `http://localhost:3000` and will proxy API requests to the backend at `http://localhost:8000`.

## Deployment to Databricks Apps

### 1. Build the Application

```bash
# Build the React frontend
npm run build

# Ensure all Python dependencies are in requirements.txt
pip freeze > requirements.txt
```

### 2. Deploy to Databricks

```bash
# Deploy using Databricks CLI
databricks apps deploy
```

The app will be deployed and accessible through your Databricks workspace.

## Configuration

### Model Serving Endpoint

The app connects to your Databricks Model Serving endpoint specified in the `SERVING_ENDPOINT` environment variable. Make sure your endpoint:

- Supports chat completion format
- Returns responses in the expected format
- Has proper authentication configured

### Dashboard Embedding

To embed your dashboard in the Dashboard tab:

1. Navigate to the Dashboard tab
2. Replace the placeholder content with your embedded dashboard
3. Update the `Dashboard.tsx` component to include your dashboard URL

Example dashboard embed:

```tsx
<iframe 
  src="https://your-dashboard-url.com" 
  width="100%" 
  height="600px" 
  frameBorder="0"
/>
```

## API Endpoints

The FastAPI backend provides the following endpoints:

- `GET /api/health` - Health check
- `POST /api/chat` - Send message to chatbot
- `GET /api/chat/history` - Get chat history
- `DELETE /api/chat/history` - Clear chat history
- `POST /api/feedback` - Submit feedback for responses
- `GET /api/dashboard-data` - Get dashboard data for charts

## Project Structure

```
informatica_app/
├── backend/
│   ├── __init__.py
│   ├── main.py
│   └── static/          # Built frontend files
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.tsx
│   │   │   ├── TabNavigation.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   └── Chat.tsx
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── index.html
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── postcss.config.js
├── package.json
├── requirements.txt
├── app.yaml
└── README.md
```

## Customization

### Styling

The app uses Tailwind CSS for styling. You can customize the theme in `frontend/tailwind.config.js`:

```javascript
theme: {
  extend: {
    colors: {
      informatica: {
        // Your brand colors
        500: '#22c55e',
      }
    }
  }
}
```

### Chat Interface

Modify the chat interface in `frontend/src/components/Chat.tsx`:

- Add new message types
- Customize the UI layout
- Add additional features like file uploads

### Dashboard

Update the dashboard in `frontend/src/components/Dashboard.tsx`:

- Add new metrics cards
- Embed different dashboards
- Add interactive charts

## Troubleshooting

### Common Issues

1. **Model Serving Connection Error**
   - Verify your `SERVING_ENDPOINT` environment variable
   - Check Databricks authentication
   - Ensure the endpoint is running and accessible

2. **Frontend Build Issues**
   - Clear node_modules and reinstall: `rm -rf node_modules && npm install`
   - Check Node.js version compatibility

3. **API Connection Issues**
   - Verify the FastAPI server is running on port 8000
   - Check CORS configuration
   - Ensure proper proxy setup in development

### Logs

Check the application logs for debugging:

```bash
# FastAPI logs
uvicorn backend.main:app --log-level debug

# Frontend logs (in browser console)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions:

- Check the Databricks documentation
- Review the app logs for error messages
- Contact the development team

---

**Built with ❤️ for Informatica**
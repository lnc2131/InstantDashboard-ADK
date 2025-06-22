# InstantDashboard Analytics - Google Apps Script Add-on

## Overview

This Google Apps Script add-on integrates your InstantDashboard backend with Google Docs, allowing users to perform AI-powered data analysis and create professional reports directly within Google Docs.

## Features

### 🔍 Data Analysis
- **Natural Language Queries**: Ask questions about your BigQuery data in plain English
- **Automatic Results**: AI-powered analysis with charts and insights
- **Schema Information**: Browse available tables and columns
- **Real-time Integration**: Direct connection to your InstantDashboard backend

### 📄 Document Integration  
- **Professional Templates**: Executive, Sales, Marketing, and Financial report templates
- **Smart Insertion**: Results inserted at cursor position or end of document
- **Formatted Tables**: Clean data presentation with proper formatting
- **Chart Recommendations**: AI-suggested visualizations for your data

### 📁 File Management (Future)
- **PDF Analysis**: Upload and analyze PDF documents
- **Google Drive Integration**: Connect to existing Drive files
- **Multi-source Reports**: Combine BigQuery data with document analysis

## Quick Start

### 1. Set Up Your Backend

First, ensure your InstantDashboard API is running:

```bash
# Navigate to your data-science directory
cd /Users/lnc/adk-samples/python/agents/data-science

# Start the API server
python api/report_writer_main.py
```

The API should be accessible at `http://localhost:8000`

### 2. Create the Apps Script Project

1. Go to [Google Apps Script](https://script.google.com)
2. Click **"New Project"**
3. Replace the default `Code.gs` with the contents of our `Code.gs` file
4. Create a new file called `appsscript.json` and paste our manifest content
5. Save the project with a meaningful name like "InstantDashboard Analytics"

### 3. Configure API Connection

In the `Code.gs` file, update the API configuration:

```javascript
// Update this URL to match your deployment
const API_BASE_URL = 'http://localhost:8000'; // or your production URL
```

For production, you'll need to deploy your API to a public URL (e.g., Google Cloud Run).

### 4. Deploy as Add-on

1. In the Apps Script editor, click **"Deploy"** → **"New Deployment"**
2. Choose type: **"Add-on"**
3. Fill in the deployment details:
   - **Description**: "AI-powered analytics for Google Docs"
   - **Version**: "1.0"
4. Click **"Deploy"**

### 5. Test in Google Docs

1. Open a new Google Doc
2. Click **"Extensions"** → **"InstantDashboard Analytics"**
3. The add-on sidebar should appear
4. Try the **"Demo Analysis"** button to test the integration

## Usage Guide

### Data Analysis Workflow

1. **Open Google Docs** and create a new document
2. **Launch the add-on** from Extensions menu
3. **Ask a question** in natural language, such as:
   - "Show me sales trends by region this quarter"
   - "What are our top 10 products by revenue?"
   - "Analyze customer churn rates by segment"
4. **Click "Analyze Data"** to process your query
5. **Review results** automatically inserted into your document

### Using Report Templates

1. **Select a template** from the dropdown:
   - **Executive Summary**: High-level business overview
   - **Sales Performance**: Sales metrics and analysis
   - **Marketing Analytics**: Campaign and customer analysis
   - **Financial Report**: Revenue, costs, and profitability
   - **Custom Analysis**: Flexible template for any analysis

2. **Click "Insert Template"** to add structure to your document
3. **Fill in sections** using the data analysis features
4. **Generate insights** with AI-powered recommendations

### Schema Exploration

1. **Click "Get Schema"** to see available data tables
2. **Review the schema** to understand what data is available
3. **Use table names** in your natural language queries

## API Integration Details

### Backend Endpoints Used

The add-on integrates with these API endpoints:

- `POST /api/apps-script/quick-query` - Main data analysis
- `GET /api/schema` - Database schema information  
- `POST /api/apps-script/auth` - Authentication (demo mode)
- `POST /api/apps-script/analyze-pdf` - PDF analysis (future)

### Response Format

The backend returns standardized responses:

```json
{
  "success": true,
  "data": [...],           // Query results (limited to 10 rows)
  "summary": "...",        // Human-readable summary
  "charts": {...},         // Chart recommendations
  "error": null            // Error message if any
}
```

### Authentication

Currently using demo authentication. For production, implement:

1. **Google OAuth**: Validate user tokens
2. **API Keys**: Secure backend access
3. **Rate Limiting**: Prevent abuse

## Development & Customization

### Adding New Features

The add-on is modular and extensible:

1. **New Templates**: Add template functions to `Code.gs`
2. **Custom Analysis**: Extend the `handleDataQuery` function
3. **UI Changes**: Modify the card creation functions
4. **API Integration**: Add new endpoints to the backend

### Local Development

1. **Use Apps Script IDE**: Edit directly in the browser
2. **Test Frequently**: Use the execution log for debugging
3. **Version Control**: Copy code to local files for backup

### Deployment Options

#### Development
- **Test Deployment**: Deploy as test add-on for personal use
- **Local API**: Connect to `localhost:8000` for development

#### Production  
- **Public Add-on**: Submit to Google Workspace Marketplace
- **Cloud API**: Deploy backend to Google Cloud Run or similar
- **Custom Domain**: Use your own domain for API access

## Troubleshooting

### Common Issues

#### "Failed to analyze data" Error
- **Check API URL**: Ensure `API_BASE_URL` is correct
- **API Status**: Verify your backend is running
- **CORS Settings**: Ensure backend allows Google Apps Script origins

#### "No data found" Response
- **Check Query**: Verify your question references available data
- **Schema Review**: Use "Get Schema" to see available tables
- **BigQuery Access**: Ensure your backend has proper BigQuery credentials

#### Add-on Not Loading
- **Permissions**: Grant required Google Workspace permissions
- **Manifest**: Check `appsscript.json` for syntax errors
- **Deployment**: Ensure add-on is properly deployed

### Debug Mode

Enable debugging in the Apps Script editor:

1. Click **"Execution Log"** to see console output
2. Add `console.log()` statements for debugging
3. Use try-catch blocks to handle errors gracefully

## Security Considerations

### Data Privacy
- **Document Access**: Add-on only accesses current document
- **API Calls**: Data sent to your own backend only
- **No Storage**: No data stored in Apps Script

### Authentication
- **Current**: Demo mode for development
- **Recommended**: Implement Google OAuth for production
- **API Security**: Use HTTPS and proper authentication

### Rate Limiting
- **Apps Script**: 6-minute execution time limit
- **API Calls**: Consider rate limiting on backend
- **User Quotas**: Monitor usage to prevent abuse

## Future Enhancements

### Phase 1 (Current)
- ✅ Basic data analysis integration
- ✅ Report templates
- ✅ Schema exploration
- ✅ Google Docs integration

### Phase 2 (Planned)
- 📄 PDF document analysis
- 📁 Google Drive file integration
- 🎨 Enhanced chart generation
- 🔐 Production authentication

### Phase 3 (Future)
- 📊 Interactive charts in documents
- 🤝 Real-time collaboration features
- 📈 Advanced analytics and forecasting
- 🏢 Enterprise features and security

## Support

### Getting Help
- **Documentation**: Refer to this README
- **API Docs**: Check FastAPI docs at `/docs` endpoint
- **Apps Script**: Google Apps Script documentation
- **BigQuery**: Google BigQuery documentation

### Contributing
- **Bug Reports**: Report issues with specific error messages
- **Feature Requests**: Suggest improvements with use cases
- **Code Contributions**: Submit pull requests with tests

---

## Quick Reference

### Key Functions
- `onDocsHomepage()` - Add-on entry point
- `handleDataQuery()` - Process data analysis requests
- `insertAnalysisResults()` - Insert results into document
- `callAPI()` - Backend API integration

### Templates Available
- Executive Summary
- Sales Performance  
- Marketing Analytics
- Financial Report
- Custom Analysis

### API Endpoints
- Quick Query: `/api/apps-script/quick-query`
- Schema Info: `/api/schema`
- Authentication: `/api/apps-script/auth`

### Permissions Required
- Google Docs access (current document only)
- Google Drive read access
- External URL access (for API calls)
- User email access (for authentication)

---

**Ready to transform how you create data-driven reports in Google Docs!** 🚀 
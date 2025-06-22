/**
 * InstantDashboard Analytics - Google Docs Add-on
 * 
 * This add-on integrates with your InstantDashboard backend to provide
 * AI-powered analytics and reporting directly in Google Docs.
 */

// Configuration - UPDATED WITH NGROK HTTPS URL
const API_BASE_URL = 'https://9383-1-34-60-197.ngrok-free.app';
const API_ENDPOINTS = {
  quickQuery: '/api/apps-script/quick-query',
  auth: '/api/apps-script/auth',
  analyzePdf: '/api/apps-script/analyze-pdf',
  schema: '/api/schema'
};

/**
 * Homepage trigger - shows when user opens the add-on
 */
function onDocsHomepage() {
  return createHomepageCard();
}

/**
 * File scope granted trigger - shows when user grants document access
 */
function onFileScopeGranted() {
  return createHomepageCard();
}

/**
 * File scope granted trigger - shows when user grants document access
 */
function onFileScopeGranted() {
  return createHomepageCard();
}

/**
 * Creates the main homepage card interface
 */
function createHomepageCard() {
  const card = CardService.newCardBuilder()
    .setHeader(CardService.newCardHeader()
      .setTitle('📊 InstantDashboard Analytics')
      .setSubtitle('AI-Powered Data Analysis')
      .setImageUrl('https://developers.google.com/apps-script/images/apps-script-logo.png')
    );

  // Add main sections
  card.addSection(createDataQuerySection());
  card.addSection(createFileUploadSection());
  card.addSection(createTemplateSection());
  
  return card.build();
}

/**
 * Creates the data query section
 */
function createDataQuerySection() {
  return CardService.newCardSection()
    .setHeader('🔍 Analyze Your Data')
    .addWidget(
      CardService.newTextInput()
        .setFieldName('dataQuestion')
        .setTitle('Ask a question about your data')
        .setHint('e.g., "Show me sales trends by region this quarter"')
        .setMultiline(true)
    )
    .addWidget(
      CardService.newButtonSet()
        .addButton(
          CardService.newTextButton()
            .setText('🚀 Analyze Data')
            .setBackgroundColor('#4285f4')
            .setOnClickAction(CardService.newAction().setFunctionName('handleDataQuery'))
        )
        .addButton(
          CardService.newTextButton()
            .setText('📋 Get Schema')
            .setOnClickAction(CardService.newAction().setFunctionName('handleGetSchema'))
        )
    );
}

/**
 * Creates the file upload section
 */
function createFileUploadSection() {
  return CardService.newCardSection()
    .setHeader('📄 Document Analysis')
    .addWidget(
      CardService.newDecoratedText()
        .setText('Upload PDFs or connect Google Drive files for analysis')
        .setWrapText(true)
    )
    .addWidget(
      CardService.newButtonSet()
        .addButton(
          CardService.newTextButton()
            .setText('📁 Browse Drive')
            .setOnClickAction(CardService.newAction().setFunctionName('handleBrowseDrive'))
        )
        .addButton(
          CardService.newTextButton()
            .setText('📊 Demo Analysis')
            .setOnClickAction(CardService.newAction().setFunctionName('handleDemoAnalysis'))
        )
    );
}

/**
 * Creates the template section
 */
function createTemplateSection() {
  return CardService.newCardSection()
    .setHeader('📝 Report Templates')
    .addWidget(
      CardService.newSelectionInput()
        .setType(CardService.SelectionInputType.DROPDOWN)
        .setTitle('Choose a report template')
        .setFieldName('reportTemplate')
        .addItem('Executive Summary', 'executive', false)
        .addItem('Sales Performance', 'sales', false)
        .addItem('Marketing Analytics', 'marketing', false)
        .addItem('Financial Report', 'financial', false)
        .addItem('Custom Analysis', 'custom', true)
    )
    .addWidget(
      CardService.newTextButton()
        .setText('📄 Insert Template')
        .setOnClickAction(CardService.newAction().setFunctionName('handleInsertTemplate'))
    );
}

/**
 * Handles data query requests
 */
function handleDataQuery(e) {
  const question = e.formInput.dataQuestion;
  
  if (!question || question.trim() === '') {
    return createErrorResponse('Please enter a question about your data');
  }

  try {
    // Call the real API with HTTPS
    const response = callAPI(API_ENDPOINTS.quickQuery, {
      question: question.trim()
    });

    if (response.success && response.data && response.data.length > 0) {
      // Insert results into document
      insertAnalysisResults(response, question);
      
      return CardService.newActionResponseBuilder()
        .setNotification(
          CardService.newNotification()
            .setText(`✅ Analysis complete! ${response.summary}`)
            .setType(CardService.NotificationType.INFO)
        )
        .build();
    } else {
      const errorMsg = response.error || 'No data found for your query';
      return createErrorResponse(errorMsg);
    }

  } catch (error) {
    console.error('Data query error:', error);
    return createErrorResponse('Failed to analyze data: ' + error.toString());
  }
}

/**
 * Handles schema requests
 */
function handleGetSchema(e) {
  try {
    const response = callAPI(API_ENDPOINTS.schema, {}, 'GET');
    
    if (response.project_id) {
      insertSchemaInfo(response);
      
      return CardService.newActionResponseBuilder()
        .setNotification(
          CardService.newNotification()
            .setText(`✅ Schema info inserted! ${response.tables_available} tables available`)
            .setType(CardService.NotificationType.INFO)
        )
        .build();
    } else {
      return createErrorResponse('Failed to retrieve schema information');
    }

  } catch (error) {
    console.error('Schema error:', error);
    return createErrorResponse('Failed to get schema: ' + error.toString());
  }
}

/**
 * Handles Drive file browsing
 */
function handleBrowseDrive(e) {
  // For now, show available Drive integration
  const doc = DocumentApp.getActiveDocument();
  const body = doc.getBody();
  
  const driveInfo = [
    '📁 Google Drive Integration',
    '',
    'Connect to your Google Drive files:',
    '• PDF documents for analysis',
    '• Spreadsheets for data connection', 
    '• Previous reports for reference',
    '',
    '🔮 Coming soon: Direct Drive file analysis!'
  ];
  
  insertTextAtCursor(driveInfo.join('\n'));
  
  return CardService.newActionResponseBuilder()
    .setNotification(
      CardService.newNotification()
        .setText('📁 Drive integration info added to document')
        .setType(CardService.NotificationType.INFO)
    )
    .build();
}

/**
 * Handles demo analysis
 */
function handleDemoAnalysis(e) {
  const demoData = {
    success: true,
    data: [
      { metric: 'Revenue', value: '$1.2M', change: '+15%' },
      { metric: 'Users', value: '45K', change: '+8%' },
      { metric: 'Conversion', value: '3.2%', change: '+0.5%' }
    ],
    summary: 'Demo analysis showing key business metrics',
    charts: {
      chart_recommendations: [
        { type: 'bar', title: 'Revenue Trends' },
        { type: 'line', title: 'User Growth' }
      ]
    }
  };
  
  insertAnalysisResults(demoData, 'Demo business metrics analysis');
  
  return CardService.newActionResponseBuilder()
    .setNotification(
      CardService.newNotification()
        .setText('📊 Demo analysis inserted!')
        .setType(CardService.NotificationType.INFO)
    )
    .build();
}

/**
 * Handles template insertion
 */
function handleInsertTemplate(e) {
  const templateType = e.formInput.reportTemplate || 'custom';
  
  const templates = {
    executive: createExecutiveTemplate(),
    sales: createSalesTemplate(),
    marketing: createMarketingTemplate(),
    financial: createFinancialTemplate(),
    custom: createCustomTemplate()
  };
  
  const template = templates[templateType] || templates.custom;
  insertTextAtCursor(template);
  
  return CardService.newActionResponseBuilder()
    .setNotification(
      CardService.newNotification()
        .setText(`📄 ${templateType} template inserted!`)
        .setType(CardService.NotificationType.INFO)
    )
    .build();
}

/**
 * Inserts analysis results into the document
 */
function insertAnalysisResults(queryResult, question) {
  const doc = DocumentApp.getActiveDocument();
  const body = doc.getBody();
  
  const results = [
    '📊 Data Analysis Results',
    '',
    `Question: ${question}`,
    `Summary: ${queryResult.summary}`,
    ''
  ];
  
  // Add data table if available
  if (queryResult.data && Array.isArray(queryResult.data) && queryResult.data.length > 0) {
    results.push('📋 Data Results:');
    results.push('');
    
    // Add table headers
    const headers = Object.keys(queryResult.data[0]);
    results.push(headers.join(' | '));
    results.push(headers.map(() => '---').join(' | '));
    
    // Add data rows (limit to 5 for readability)
    const dataRows = queryResult.data.slice(0, 5);
    dataRows.forEach(row => {
      const values = headers.map(header => String(row[header] || ''));
      results.push(values.join(' | '));
    });
    
    if (queryResult.data.length > 5) {
      results.push(`... and ${queryResult.data.length - 5} more rows`);
    }
    results.push('');
  }
  
  // Add chart recommendations if available
  if (queryResult.charts && queryResult.charts.chart_recommendations) {
    results.push('📈 Recommended Charts:');
    queryResult.charts.chart_recommendations.forEach(chart => {
      results.push(`• ${chart.type}: ${chart.title}`);
    });
    results.push('');
  }
  
  results.push(`Generated on: ${new Date().toLocaleString()}`);
  results.push('---');
  results.push('');
  
  insertTextAtCursor(results.join('\n'));
}

/**
 * Inserts schema information into the document
 */
function insertSchemaInfo(schemaData) {
  const info = [
    '🗄️ Database Schema Information',
    '',
    `Project ID: ${schemaData.project_id}`,
    `Dataset ID: ${schemaData.dataset_id}`,
    `Available Tables: ${schemaData.tables_available}`,
    '',
    'Schema Preview:',
    '```',
    schemaData.schema.substring(0, 500) + '...',
    '```',
    '',
    `Retrieved on: ${new Date().toLocaleString()}`,
    '---',
    ''
  ];
  
  insertTextAtCursor(info.join('\n'));
}

/**
 * Inserts text at cursor position or end of document
 */
function insertTextAtCursor(text) {
  const doc = DocumentApp.getActiveDocument();
  const cursor = doc.getCursor();
  
  if (cursor) {
    // Insert at cursor position
    const element = cursor.getElement();
    const offset = cursor.getOffset();
    
    if (element.getType() === DocumentApp.ElementType.TEXT) {
      element.asText().insertText(offset, text + '\n');
    } else {
      // Insert as new paragraph
      const parent = element.getParent();
      const index = parent.getChildIndex(element);
      parent.insertParagraph(index + 1, text);
    }
  } else {
    // Insert at end of document
    doc.getBody().appendParagraph(text);
  }
}

/**
 * Makes API calls to the backend
 */
function callAPI(endpoint, payload = {}, method = 'POST') {
  const url = API_BASE_URL + endpoint;
  
  const options = {
    method: method,
    headers: {
      'Content-Type': 'application/json',
      'ngrok-skip-browser-warning': 'true'
    },
    muteHttpExceptions: true
  };
  
  if (method === 'POST' && Object.keys(payload).length > 0) {
    options.payload = JSON.stringify(payload);
  }
  
  const response = UrlFetchApp.fetch(url, options);
  const responseText = response.getContentText();
  
  try {
    return JSON.parse(responseText);
  } catch (e) {
    throw new Error(`API call failed: ${response.getResponseCode()} - ${responseText}`);
  }
}

/**
 * Creates error response
 */
function createErrorResponse(message) {
  return CardService.newActionResponseBuilder()
    .setNotification(
      CardService.newNotification()
        .setText('❌ ' + message)
        .setType(CardService.NotificationType.ERROR)
    )
    .build();
}

// Report template functions
function createExecutiveTemplate() {
  return `
# Executive Summary Report

## Key Performance Indicators
- Revenue: [Insert data analysis]
- Growth Rate: [Insert data analysis]
- Market Share: [Insert data analysis]

## Strategic Insights
[Use InstantDashboard to analyze key business metrics]

## Recommendations
[AI-generated recommendations will appear here]

## Action Items
- [ ] Review Q1 performance
- [ ] Analyze customer segments
- [ ] Plan Q2 strategy

---
Generated with InstantDashboard Analytics
`;
}

function createSalesTemplate() {
  return `
# Sales Performance Report

## Sales Metrics Overview
[Insert quarterly sales analysis]

## Regional Performance
[Analyze sales by region]

## Product Performance  
[Analyze sales by product category]

## Sales Team Performance
[Analyze individual and team metrics]

## Pipeline Analysis
[Analyze sales pipeline and forecasts]

## Recommendations
[AI-generated sales recommendations]

---
Generated with InstantDashboard Analytics
`;
}

function createMarketingTemplate() {
  return `
# Marketing Analytics Report

## Campaign Performance
[Analyze marketing campaign effectiveness]

## Customer Acquisition
[Analyze customer acquisition metrics]

## Channel Performance
[Analyze performance by marketing channel]

## ROI Analysis
[Calculate and analyze marketing ROI]

## Customer Insights
[Analyze customer behavior and segmentation]

## Recommendations
[AI-generated marketing recommendations]

---
Generated with InstantDashboard Analytics
`;
}

function createFinancialTemplate() {
  return `
# Financial Analysis Report

## Revenue Analysis
[Analyze revenue trends and forecasts]

## Cost Analysis
[Analyze cost structure and trends]

## Profitability Analysis
[Analyze profit margins and efficiency]

## Budget vs Actual
[Compare budget to actual performance]

## Financial Ratios
[Calculate and analyze key financial ratios]

## Recommendations
[AI-generated financial recommendations]

---
Generated with InstantDashboard Analytics
`;
}

function createCustomTemplate() {
  return `
# Custom Analytics Report

## Objective
[Define the purpose of this analysis]

## Data Sources
[List the data sources being analyzed]

## Key Questions
1. [Insert your analytical questions]
2. [Use InstantDashboard to find answers]
3. [Generate insights and recommendations]

## Analysis Section 1
[Insert data analysis here]

## Analysis Section 2
[Insert additional analysis here]

## Insights & Recommendations
[AI-generated insights will appear here]

## Next Steps
- [ ] [Action item 1]
- [ ] [Action item 2]

---
Generated with InstantDashboard Analytics
`;
} 
# Web Interface Guide

## 🌐 **Modern Web Frontend for Google Maps Business Scraper**

Your scraper now has a beautiful, responsive web interface that makes it easy to configure and monitor scraping operations.

## 🚀 **Quick Start**

### Start the Web Interface:
```bash
# Option 1: Using the run script
./run.sh web

# Option 2: Direct Python
source venv/bin/activate
python start_web.py
```

### Access the Interface:
- **URL**: http://localhost:5000
- **Auto-opens**: Browser will open automatically
- **Mobile-friendly**: Responsive design works on all devices

## 🎛️ **Interface Features**

### **Configuration Panel**
- **Industry Input**: Enter any industry as free text
  - **Pre-configured**: restaurants, retail, healthcare, professional services
  - **Custom Industries**: Enter any industry (e.g., automotive, fitness, beauty, technology)
  - **Auto-suggestions**: Dropdown suggestions as you type
  - **Examples**: Real estate, entertainment, education, consulting, etc.

- **Location Selection**: Multi-select from major UK cities
  - London, Manchester, Birmingham, Leeds
  - Glasgow, Liverpool, Newcastle, Sheffield
  - Bristol, Edinburgh

- **Options**: 
  - ✅ Companies House verification (recommended)
  - ⚙️ Advanced settings (coming soon)

### **Real-time Status Monitoring**
- **Progress Bar**: Visual progress indicator
- **Live Counters**: 
  - 📊 Total businesses found
  - 💾 Saved to database
  - ✅ Companies House verified
  - ❌ Errors encountered

- **Current Task**: Shows what the scraper is doing
- **Auto-refresh**: Updates every second during scraping

### **Results Dashboard**
- **Summary Statistics**: Key metrics at a glance
- **Error Logging**: Detailed error information
- **Export Options**: Download data in CSV/JSON format
- **Report Generation**: Business intelligence reports

## 🎨 **Design Features**

### **Modern UI/UX**
- **Tailwind CSS**: Clean, professional styling
- **Font Awesome Icons**: Intuitive visual indicators
- **Gradient Headers**: Eye-catching design
- **Card Layout**: Organized information display
- **Hover Effects**: Interactive elements

### **Responsive Design**
- **Mobile-first**: Works on phones and tablets
- **Grid Layout**: Adapts to different screen sizes
- **Touch-friendly**: Optimized for touch interfaces

### **Real-time Updates**
- **Live Status**: No page refresh needed
- **Progress Tracking**: Visual feedback during scraping
- **Error Handling**: Immediate error notifications

## 🔧 **Technical Features**

### **Backend (Flask)**
- **RESTful API**: Clean API endpoints
- **Async Processing**: Non-blocking scraping operations
- **Thread Safety**: Multiple users can monitor progress
- **Error Handling**: Robust error management

### **Frontend (Vanilla JavaScript)**
- **No Dependencies**: Pure JavaScript, no frameworks
- **AJAX Requests**: Smooth data updates
- **Form Validation**: Client-side input validation
- **Status Polling**: Real-time progress updates

## 📱 **Usage Instructions**

### **1. Start Scraping**
1. Select an industry from the dropdown
2. Choose one or more locations (checkboxes)
3. Ensure "Verify with Companies House" is checked
4. Click "Start Scraping"

### **2. Monitor Progress**
- Watch the progress bar fill up
- Monitor the live counters
- Check the current task status
- Review any errors in real-time

### **3. Export Results**
- Click "Export CSV" for spreadsheet format
- Click "Export JSON" for programmatic use
- Click "Generate Report" for business intelligence

### **4. Stop Scraping**
- Click "Stop Scraping" to halt the process
- Progress will be saved up to the stop point

## 🛠️ **API Endpoints**

The web interface uses these REST endpoints:

- **`POST /api/start_scraping`**: Start a new scraping job
- **`GET /api/status`**: Get current scraping status
- **`POST /api/stop_scraping`**: Stop the current job
- **`GET /api/export/{format}`**: Export data (CSV/JSON)
- **`GET /api/report`**: Generate business report

## 🔒 **Security Features**

- **Input Validation**: All inputs are validated
- **CORS Enabled**: Cross-origin requests handled
- **Error Sanitization**: Safe error message display
- **Rate Limiting**: Built-in request throttling

## 🚀 **Advanced Features**

### **Multi-user Support**
- Multiple users can monitor the same scraping job
- Real-time status updates for all connected users
- No conflicts between different users

### **Background Processing**
- Scraping runs in background threads
- Web interface remains responsive
- Can handle long-running scraping jobs

### **Data Persistence**
- All scraping results saved to database
- Progress tracking across sessions
- Export functionality for all collected data

## 🐛 **Troubleshooting**

### **Common Issues**

1. **Port 5000 in use**:
   ```bash
   # Kill process using port 5000
   lsof -ti:5000 | xargs kill -9
   ```

2. **Browser doesn't open**:
   - Manually navigate to http://localhost:5000
   - Check firewall settings

3. **Scraping doesn't start**:
   - Verify API keys in .env file
   - Check database connection
   - Review error messages in status panel

### **Debug Mode**
```bash
# Run with debug output
FLASK_DEBUG=1 python app.py
```

## 📊 **Performance**

- **Lightweight**: Minimal resource usage
- **Fast Loading**: Optimized CSS and JavaScript
- **Efficient Updates**: Only necessary data refreshed
- **Scalable**: Can handle multiple concurrent users

## 🔮 **Future Enhancements**

- **Scheduled Scraping**: Set up recurring jobs
- **Advanced Filters**: More granular search options
- **Data Visualization**: Charts and graphs
- **User Authentication**: Multi-user accounts
- **API Documentation**: Interactive API explorer

## 💡 **Tips for Best Results**

1. **Start Small**: Test with 1-2 locations first
2. **Monitor Progress**: Keep an eye on error counts
3. **Export Regularly**: Download data periodically
4. **Check Logs**: Review error messages for issues
5. **Use Companies House**: Always enable verification

The web interface makes your Google Maps scraper accessible to non-technical users while providing powerful monitoring and control capabilities for advanced users!

# 🌊 Ocean Data Explorer Chatbot - Streamlit Dashboard

A comprehensive interactive chatbot dashboard for exploring oceanographic data from Argo floats using natural language queries.

## 🚀 Features

- **🤖 Natural Language Chatbot**: Ask questions about ocean data in plain English
- **Interactive Ocean Data Visualization**: Explore temperature, salinity, and pressure data from major ocean regions
- **Real-time Argo Data Fetching**: Direct integration with ArgoVis API for up-to-date ocean measurements  
- **Multiple Visualization Types**:
  - Vertical profiles (Temperature & Salinity vs Depth)
  - Depth-time curtain plots
  - Temperature-Salinity diagrams
  - Surface temperature maps
  - Variable distribution histograms
- **Interactive Maps**: Folium-based maps with Argo float locations and heat maps
- **Data Export**: Download processed data as CSV files
- **Responsive Design**: Clean, modern interface optimized for desktop and mobile

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Instructions

1. **Clone or download the project files**
   ```bash
   # If using git
   git clone <repository-url>
   cd SIH(Final)
   
   # Or simply download the files to a folder
   ```

2. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the dashboard**
   ```bash
   streamlit run ocean_data_dashboard.py
   ```

4. **Access the dashboard**
   - Open your web browser
   - Navigate to `http://localhost:8501`
   - The dashboard will load automatically

## 📖 Usage Guide

### Getting Started

1. **Ask Your Question**: Type your ocean data question in natural language in the chatbot interface
   - Example: *"Show me temperature in the Indian Ocean from 2024-06-01 to 2024-06-15"*

2. **Choose Visualization**: Use the sidebar to select what you want to see:
   - **Graphs Only**: Display all analytical plots
   - **Map Only**: Show interactive map with float locations  
   - **Both**: Display complete visualization suite

3. **Fetch Data**: Click "Fetch Ocean Data" to retrieve and process Argo float measurements

#### 🤖 Example Chatbot Queries:
- *"Display salinity data for North Atlantic in June 2024"*
- *"I want to see temperature and pressure in the Pacific Ocean"*  
- *"Show all variables for Southern Ocean in July 2024"*
- *"Temperature data in South Atlantic from 2024-05-01 to 2024-05-30"*

The chatbot automatically extracts:
- **Region**: Indian Ocean, Atlantic, Pacific, etc.
- **Variables**: Temperature, Salinity, Pressure (or all if not specified)
- **Date Range**: Specific dates or month/year periods

### Understanding the Visualizations

#### 📊 Graphs Section
- **Vertical Profiles**: Shows how temperature and salinity change with depth
- **Depth-Time Curtain**: Displays temperature evolution over time and depth
- **T-S Diagram**: Reveals water mass characteristics through temperature-salinity relationships  
- **Surface Temperature Map**: Visualizes sea surface temperature distribution
- **Variable Distributions**: Statistical histograms of measured parameters

#### 🗺️ Interactive Map
- **Float Markers**: Color-coded by operational status (Active/Inactive/Unknown)
- **Region Boundaries**: Yellow rectangle showing selected search area
- **Temperature Heatmap**: Optional overlay showing temperature distribution
- **Detailed Popups**: Click markers for float-specific information

### Data Export
- **CSV Download**: Export processed data for external analysis
- **Map Save**: Save interactive maps as HTML files for sharing

## 🔧 Technical Details

### Architecture
- **Frontend**: Streamlit web framework
- **Data Source**: ArgoVis API via argopy library
- **Visualization**: Matplotlib, Plotly, Folium
- **Caching**: Streamlit's built-in caching for improved performance

### Data Processing
- Automatic column mapping for different data formats
- Quality control filtering (removes NaN values)
- Sampling for large datasets to optimize performance
- Real-time coordinate transformation and validation

### Performance Optimizations
- **Data Caching**: 1-hour TTL cache for API responses
- **Sample Limiting**: Intelligent sampling for large datasets
- **Lazy Loading**: Visualizations generated on-demand
- **Memory Management**: Efficient pandas operations

## 🌊 Ocean Regions Available

| Region | Longitude Range | Latitude Range |
|--------|----------------|----------------|
| Indian Ocean | 20°E to 120°E | 60°S to 30°N |
| North Atlantic | 80°W to 0° | 0° to 60°N |
| South Atlantic | 70°W to 20°E | 60°S to 0° |
| North Pacific | 120°E to 240°E | 0° to 60°N |
| South Pacific | 120°E to 290°E | 60°S to 0° |
| Southern Ocean | 180°W to 180°E | 90°S to 60°S |

## 🔍 Troubleshooting

### Common Issues

**No Data Found**
- Try expanding your date range
- Select a different region
- Check internet connection for API access

**Slow Performance**  
- Large datasets may take time to process
- Consider using shorter date ranges
- Visualizations are cached for better performance

**Map Not Loading**
- Ensure stable internet connection
- Try refreshing the page
- Check if folium and streamlit-folium are properly installed

### Error Messages
- **"Missing latitude or longitude columns"**: Data format issue, try different date range
- **"Error fetching data"**: Network or API issue, check connection and try again

## 📚 Dependencies

- `streamlit>=1.28.0` - Web app framework
- `pandas>=1.5.0` - Data manipulation
- `numpy>=1.24.0` - Numerical computing  
- `matplotlib>=3.6.0` - Static plotting
- `plotly>=5.15.0` - Interactive plotting
- `seaborn>=0.12.0` - Statistical visualization
- `folium>=0.14.0` - Interactive mapping
- `streamlit-folium>=0.13.0` - Folium integration
- `argopy>=0.1.13` - Argo data access

## 🤝 Contributing

This dashboard is part of the Smart India Hackathon project for ocean data visualization. 

### Development Setup
1. Fork the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Make your changes
4. Test thoroughly with different regions and date ranges
5. Submit pull request with detailed description

## 📄 License

This project is developed for educational and research purposes as part of the Smart India Hackathon initiative.

## 🆘 Support

For technical issues or questions:
1. Check the troubleshooting section above
2. Verify all dependencies are correctly installed
3. Ensure stable internet connection for data fetching
4. Review error messages in the Streamlit interface

---

**Built with ❤️ for Ocean Data Exploration**
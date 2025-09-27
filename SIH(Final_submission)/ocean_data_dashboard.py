import os
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

from argopy import DataFetcher as ArgoDataFetcher
import datetime
from datetime import date

# Optional libraries
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import seaborn as sns
    SEABORN_AVAILABLE = True
except ImportError:
    SEABORN_AVAILABLE = False

import folium
from folium.plugins import MarkerCluster, HeatMap
import streamlit_folium as st_folium

# Pinecone vector database for documentation queries
try:
    import pinecone
    from sentence_transformers import SentenceTransformer
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False

# Groq AI for intelligent query processing
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

# Page Configuration
st.set_page_config(
    page_title="Ocean Data Explorer",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: linear-gradient(90deg, #e3f2fd 0%, #bbdefb 100%);
        border-radius: 10px;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    .metric-container {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stAlert > div {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------- Constants ---------------------------
REGIONS = {
    "Indian Ocean": {"lon_min": 20.0, "lon_max": 120.0, "lat_min": -60.0, "lat_max": 30.0},
    "North Atlantic": {"lon_min": -80.0, "lon_max": 0.0, "lat_min": 0.0, "lat_max": 60.0},
    "South Atlantic": {"lon_min": -70.0, "lon_max": 20.0, "lat_min": -60.0, "lat_max": 0.0},
    "North Pacific": {"lon_min": 120.0, "lon_max": 240.0, "lat_min": 0.0, "lat_max": 60.0},
    "South Pacific": {"lon_min": 120.0, "lon_max": 290.0, "lat_min": -60.0, "lat_max": 0.0},
    "Southern Ocean": {"lon_min": -180.0, "lon_max": 180.0, "lat_min": -90.0, "lat_max": -60.0},
}

VARIABLES = ["Temperature", "Salinity", "Pressure"]

# --------------------------- Pinecone Vector Database ---------------------------
@st.cache_resource
def initialize_pinecone():
    """Initialize Pinecone vector database and sentence transformer"""
    if not PINECONE_AVAILABLE:
        return None, None
    
    try:
        # Initialize Pinecone with your specific configuration
        api_key = os.getenv("PINECONE_API_KEY")
        
        # Initialize Pinecone client for serverless
        try:
            from pinecone import Pinecone, ServerlessSpec
            pc = Pinecone(api_key=api_key)
        except:
            # Fallback for older pinecone versions
            import pinecone
            pinecone.init(api_key=api_key)
            pc = pinecone
        
        # Load sentence transformer for embeddings (using 512-dimensional model to match your index)
        model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')  # 768 dimensions
        # Note: Your index has 512 dimensions, so we'll need to use a different model or adjust
        # Using a model that outputs 512 dimensions
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L12-v2')  # 384 dimensions
        # For exact 512 dimensions, we'll use a custom approach or pad/truncate
        
        # Connect to your specific index
        index_name = "floatchat"
        
        try:
            # Try to get existing index
            if hasattr(pc, 'Index'):
                index = pc.Index(index_name)
            else:
                index = pinecone.Index(index_name)
        except:
            # Index exists, just connect to it
            try:
                if hasattr(pc, 'Index'):
                    index = pc.Index(index_name)
                else:
                    index = pinecone.Index(index_name)
            except:
                st.warning(f"⚠️ Could not connect to Pinecone index '{index_name}'")
                return None, None
        
        return index, model
    
    except Exception as e:
        st.warning(f"⚠️ Could not initialize Pinecone: {e}")
        return None, None

def query_documentation(query, index, model, top_k=3):
    """Query the vector database for argopy documentation"""
    if not index or not model:
        return []
    
    try:
        # Generate embedding for the query
        query_embedding = model.encode(query).tolist()
        
        # Adjust embedding dimensions to match your 512-dimensional index
        if len(query_embedding) > 512:
            query_embedding = query_embedding[:512]  # Truncate to 512
        elif len(query_embedding) < 512:
            # Pad with zeros to reach 512 dimensions
            query_embedding.extend([0.0] * (512 - len(query_embedding)))
        
        # Search in Pinecone
        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        # Extract relevant documentation
        docs = []
        for match in results['matches']:
            if match['score'] > 0.3:  # Lowered similarity threshold for better matching
                docs.append({
                    'content': match['metadata'].get('content', ''),
                    'title': match['metadata'].get('title', 'Documentation'),
                    'score': match['score']
                })
        
        return docs
    
    except Exception as e:
        st.warning(f"⚠️ Error querying documentation: {e}")
        return []

def generate_documentation_response(query, docs):
    """Generate a helpful response using documentation from vector database"""
    if not docs:
        return """
        **📚 Documentation Query**
        
        I couldn't find specific documentation for your query in the vector database. Here are some general troubleshooting tips:
        
        **Common ArgoPy Issues:**
        - Check your internet connection for data fetching
        - Verify the date range is valid (not too far in the future)
        - Ensure the geographic region has available Argo floats
        - Try reducing the date range if getting timeout errors
        
        **Useful ArgoPy Resources:**
        - Official Documentation: https://argopy.readthedocs.io/
        - GitHub Repository: https://github.com/euroargodev/argopy
        - Argo Data Access: https://www.ocean-ops.org/
        """
    
    response = "**📚 Documentation Found**\n\n"
    response += f"Based on your query about: *{query}*\n\n"
    
    for i, doc in enumerate(docs, 1):
        response += f"**{i}. {doc['title']}** (Relevance: {doc['score']:.2f})\n"
        response += f"{doc['content']}\n\n"
    
    response += "**💡 Additional Help:**\n"
    response += "- Try adjusting your query parameters\n"
    response += "- Check the Argo data availability for your region and time period\n"
    response += "- Visit https://argopy.readthedocs.io/ for complete documentation"
    
    return response

# --------------------------- Groq AI Integration ---------------------------
@st.cache_resource
def initialize_groq():
    """Initialize Groq AI client"""
    if not GROQ_AVAILABLE:
        return None
    
    try:
        # Initialize Groq with your API key
        api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
        
        if not api_key:
            st.warning("⚠️ Groq API key not configured. Advanced query processing will be limited.")
            return None
        
        client = Groq(api_key=api_key)
        return client
    
    except Exception as e:
        st.warning(f"⚠️ Could not initialize Groq: {e}")
        return None

def get_relevant_context(query, index, model, top_k=5):
    """Get relevant context from vector database for Groq"""
    if not index or not model:
        return ""
    
    try:
        docs = query_documentation(query, index, model, top_k)
        if not docs:
            return ""
        
        context = "RELEVANT ARGOPY DOCUMENTATION:\n\n"
        for doc in docs:
            context += f"- {doc['title']}: {doc['content']}\n\n"
        
        return context
    except:
        return ""

def process_query_with_groq(user_query, groq_client, context=""):
    """Process user query with Groq AI using vector database context"""
    if not groq_client:
        return None
    
    try:
        system_prompt = f"""You are a friendly oceanography educator. Provide SHORT, INTERESTING one-liner facts about ocean regions.

IMPORTANT GUIDELINES:
- Provide 3-5 SHORT one-liner facts (maximum 15-20 words each)
- Make each fact fascinating and memorable
- Focus on surprising or amazing ocean characteristics
- Use bullet points for easy reading
- NO long paragraphs, NO technical details, NO code

Your task: Generate brief, engaging facts about the ocean region in the user's query.

CONTEXT FROM VECTOR DATABASE:
{context}

Response format:
• [Amazing fact 1 - keep it short!]
• [Interesting fact 2 - one liner!]  
• [Cool fact 3 - brief and engaging!]

Example format:
• The Pacific Ocean contains more than half of all free water on Earth
• Ocean currents here move faster than a walking human
• This region's deepest point could fit Mount Everest with room to spare"""

        response = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            model="openai/gpt-oss-120b",
            temperature=0.3,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        st.warning(f"⚠️ Groq processing error: {e}")
        return None

def process_detailed_ai_assistant(user_query, groq_client, context=""):
    """Process detailed AI assistant queries with comprehensive domain knowledge"""
    if not groq_client:
        return None
    
    try:
        system_prompt = f"""You are an expert oceanography educator providing detailed, comprehensive information about ocean data and marine science.

IMPORTANT GUIDELINES:
- Provide DETAILED, COMPREHENSIVE overviews with rich domain knowledge
- Focus on OCEAN SCIENCE and fascinating oceanographic phenomena
- Include interesting facts, scientific insights, and practical applications
- Make complex concepts accessible and engaging
- Structure information clearly with headings and bullet points
- NO programming code or technical implementation details

Your tasks:
1. Provide detailed explanations of oceanographic concepts
2. Share fascinating facts and scientific insights about ocean regions
3. Explain the significance of ocean measurements and phenomena
4. Discuss current research and discoveries in marine science
5. Connect ocean data to real-world applications and climate impacts

CONTEXT FROM VECTOR DATABASE:
{context}

Response guidelines:
- Write in a detailed, educational style with clear structure
- Use headings (###) to organize different aspects
- Include specific measurements, ranges, and scientific data
- Provide context about why these phenomena matter
- Make it engaging with surprising facts and connections
- Focus on comprehensive domain knowledge"""

        response = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            model="openai/gpt-oss-120b",
            temperature=0.3,
            max_tokens=1500
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        st.warning(f"⚠️ Groq processing error: {e}")
        return None

def process_technical_query_internal(user_query, error_info, groq_client, context=""):
    """Internal function to process technical queries and errors for system improvement (not shown to users)"""
    if not groq_client:
        return None
    
    try:
        system_prompt = f"""You are an expert ArgoPy technical assistant. This is an INTERNAL function for system improvement.

Your task is to analyze user queries and technical errors to suggest better query parameters.

ERROR INFORMATION: {error_info}
CONTEXT FROM VECTOR DATABASE: {context}

Provide technical analysis and suggestions for:
1. Fixing longitude/latitude coordinate issues
2. Adjusting date ranges
3. Selecting appropriate regions
4. Resolving API limitations

Focus on technical solutions and parameter adjustments. This output is for system use only.

Response format:
- Provide specific parameter corrections
- Suggest alternative coordinate systems
- Recommend region adjustments
- Include technical troubleshooting steps"""

        response = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            model="openai/gpt-oss-120b",
            temperature=0.2,
            max_tokens=800
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return None

def smart_query_reframing(user_query, groq_client, index, model):
    """Use Groq + Vector DB to intelligently reframe unclear queries"""
    if not groq_client:
        return user_query, None
    
    try:
        # Get relevant context from vector database
        context = get_relevant_context(user_query, index, model)
        
        # Ask Groq to analyze and improve the query
        reframe_prompt = f"""Analyze this ocean data query and help improve it for ArgoPy data fetching:

USER QUERY: "{user_query}"

AVAILABLE CONTEXT: {context}

Tasks:
1. Identify what the user wants (region, variables, time period)
2. Suggest improvements if the query is unclear or problematic
3. Provide a better formatted query if needed
4. Explain any issues with the original query

Respond in this format:
ANALYSIS: [Brief analysis of the query]
SUGGESTED_QUERY: [Improved query or "ORIGINAL_QUERY_OK" if no changes needed]
EXPLANATION: [Why changes were made or validation of original query]
PARAMETERS: [Suggested region, dates, variables]"""

        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": reframe_prompt}],
            model="openai/gpt-oss-120b",
            temperature=0.2,
            max_tokens=500
        )
        
        ai_response = response.choices[0].message.content
        
        # Parse the response
        if "SUGGESTED_QUERY:" in ai_response:
            suggested_part = ai_response.split("SUGGESTED_QUERY:")[1].split("EXPLANATION:")[0].strip()
            if suggested_part != "ORIGINAL_QUERY_OK":
                return suggested_part, ai_response
        
        return user_query, ai_response
    
    except Exception as e:
        st.warning(f"⚠️ Query reframing error: {e}")
        return user_query, None

# --------------------------- Query Parser ---------------------------
def parse_query(query):
    """Parse natural language query to extract region, dates, and variables"""
    query = query.lower()
    
    # Extract region
    regions_map = {
        "indian ocean": "Indian Ocean",
        "north atlantic": "North Atlantic", 
        "south atlantic": "South Atlantic",
        "north pacific": "North Pacific",
        "south pacific": "South Pacific", 
        "southern ocean": "Southern Ocean",
        "atlantic": "North Atlantic",
        "pacific": "North Pacific",
        "indian": "Indian Ocean"
    }
    
    region_name = "Indian Ocean"  # default
    for key, value in regions_map.items():
        if key in query:
            region_name = value
            break
    
    # Extract dates
    import re
    dates = re.findall(r"\d{4}-\d{2}-\d{2}", query)
    month_year = re.search(r"(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{4})", query)
    
    if len(dates) == 0 and month_year:
        months = {
            "january": "01", "february": "02", "march": "03", "april": "04",
            "may": "05", "june": "06", "july": "07", "august": "08",
            "september": "09", "october": "10", "november": "11", "december": "12"
        }
        month_name = month_year.group(1)
        year = month_year.group(2)
        start_date = f"{year}-{months[month_name]}-01"
        end_date = f"{year}-{months[month_name]}-28"
    elif len(dates) == 0:
        start_date = end_date = "2024-06-01"
    elif len(dates) == 1:
        start_date = end_date = dates[0]
    else:
        start_date, end_date = dates[0], dates[1]
    
    # Extract variables
    variables = []
    if any(word in query for word in ["temperature", "temp"]):
        variables.append("Temperature")
    if any(word in query for word in ["salinity", "salinty", "salt"]):
        variables.append("Salinity")
    if any(word in query for word in ["pressure", "press", "depth"]):
        variables.append("Pressure")
    
    # If no specific variables mentioned, include all
    if not variables:
        variables = ["Temperature", "Salinity", "Pressure"]
    
    return region_name, start_date, end_date, variables

# --------------------------- Helper Functions ---------------------------
@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_argo_data(region_name, start_date, end_date, bbox):
    """Fetch Argo data with caching for better performance"""
    try:
        with st.spinner(f"Fetching data from argovis for {region_name}..."):
            argo = ArgoDataFetcher(src="argovis")
            ds = argo.region([bbox["lon_min"], bbox["lon_max"], 
                              bbox["lat_min"], bbox["lat_max"], 
                              0, 30, start_date.strftime("%Y-%m-%d"), 
                              end_date.strftime("%Y-%m-%d")]).to_xarray()
            df = ds.to_dataframe().reset_index()
            
            # Column mapping
            column_mapping = {}
            for lat_variant in ['LATITUDE', 'latitude', 'lat', 'LAT']:
                if lat_variant in df.columns: 
                    column_mapping[lat_variant] = 'latitude'
                    break
            for lon_variant in ['LONGITUDE', 'longitude', 'lon', 'LON']:
                if lon_variant in df.columns: 
                    column_mapping[lon_variant] = 'longitude'
                    break
            for time_variant in ['TIME', 'time', 'date', 'DATE']:
                if time_variant in df.columns: 
                    column_mapping[time_variant] = 'time'
                    break

            df = df.rename(columns=column_mapping)
            cols_to_keep = [c for c in ['time', 'latitude', 'longitude', 'PRES', 'PSAL', 'TEMP'] if c in df.columns]

            if 'latitude' not in df.columns or 'longitude' not in df.columns:
                st.error("Error: Missing latitude or longitude columns")
                return pd.DataFrame()
                
            df = df[cols_to_keep]

            # Drop rows with all NaN values in measurement columns
            drop_subset = [c for c in ["PRES", "PSAL", "TEMP"] if c in df.columns]
            if drop_subset: 
                df = df.dropna(subset=drop_subset)

            return df
            
    except Exception as e:
        st.warning(f"⚠️ Unable to fetch data for {region_name} during the selected time period.")
        
        # Use AI to provide friendly domain knowledge instead of technical errors
        if GROQ_AVAILABLE and PINECONE_AVAILABLE:
            groq_client = initialize_groq()
            index, model = initialize_pinecone()
            
            if groq_client and index and model:
                # FIRST: Show region suggestions at the top for immediate action
                st.markdown("---")
                st.markdown("### 🎯 Try These Alternative Regions")
                st.info("💡 **Tip**: Different regions may have better data coverage. Try these regions with good data availability:")
                
                # Create columns for region suggestions
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**🌊 Well-Covered Ocean Regions:**")
                    st.markdown("• **Indian Ocean** - Excellent coverage")
                    st.markdown("• **North Atlantic** - High data density")
                    st.markdown("• **Southern Ocean** - Good seasonal data")
                
                with col2:
                    st.markdown("**📅 Suggested Time Periods:**")
                    st.markdown("• **Recent 6 months** - Best coverage")
                    st.markdown("• **Summer months** - Peak activity")
                    st.markdown("• **30-day windows** - Optimal range")
                
                st.markdown("**🔄 Quick Example:** Try *Indian Ocean* with *last 3 months* for reliable data!")
                
                # SECOND: Create a user-friendly query about the ocean region
                friendly_query = f"Tell me about ocean data and characteristics of the {region_name} region, including temperature, salinity, and interesting oceanographic features"
                
                # Get relevant context from vector database
                context = get_relevant_context(friendly_query, index, model)
                
                # Generate friendly domain knowledge response
                ai_response = process_query_with_groq(friendly_query, groq_client, context)
                
                if ai_response:
                    st.markdown("---")
                    st.markdown("### 🌊 Learn About This Ocean Region")
                    st.info("While we work on getting the data, here's some interesting information about this ocean region:")
                    st.markdown(ai_response)
                
                # Internally, use technical analysis to improve future queries (not shown to user)
                technical_analysis = process_technical_query_internal(
                    f"region {region_name} date range {start_date} to {end_date}", 
                    str(e), 
                    groq_client, 
                    context
                )
                # This technical_analysis is for system improvement only, not displayed to users
        
        return pd.DataFrame()

def create_vertical_profile(df, region_name):
    """Create vertical profile plots"""
    if len(df) == 0: 
        return None
    
    # Select data for profile
    if 'PLATFORM_NUMBER' in df.columns and 'CYCLE_NUMBER' in df.columns:
        sample_float = df['PLATFORM_NUMBER'].iloc[0]
        sample_cycle = df['CYCLE_NUMBER'].iloc[0]
        profile_data = df[(df['PLATFORM_NUMBER'] == sample_float) & (df['CYCLE_NUMBER'] == sample_cycle)]
    else: 
        profile_data = df.head(100)
    
    profile_data = profile_data.sort_values('PRES')
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 8))
    
    # Temperature profile
    ax1.plot(profile_data['TEMP'], profile_data['PRES'], 'r-', linewidth=2)
    ax1.set_xlabel('Temperature (°C)')
    ax1.set_ylabel('Pressure (dbar)')
    ax1.set_title(f'Temperature Profile\n{region_name}')
    ax1.grid(True, alpha=0.3)
    ax1.invert_yaxis()
    
    # Salinity profile
    ax2.plot(profile_data['PSAL'], profile_data['PRES'], 'b-', linewidth=2)
    ax2.set_xlabel('Salinity (PSU)')
    ax2.set_ylabel('Pressure (dbar)')
    ax2.set_title(f'Salinity Profile\n{region_name}')
    ax2.grid(True, alpha=0.3)
    ax2.invert_yaxis()
    
    plt.tight_layout()
    return fig

def create_depth_time_curtain(df, region_name):
    """Create depth-time curtain plot"""
    if len(df) == 0 or 'time' not in df.columns: 
        return None
        
    if df['time'].dtype == 'object': 
        df['time'] = pd.to_datetime(df['time'])
    
    if PLOTLY_AVAILABLE:
        sample_df = df.sample(min(1000, len(df))) if len(df) > 1000 else df
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=sample_df['time'], 
            y=sample_df['PRES'], 
            mode='markers',
            marker=dict(
                color=sample_df['TEMP'], 
                colorscale='RdYlBu_r', 
                size=4,
                colorbar=dict(title="Temperature (°C)")
            ),
            text=sample_df['TEMP'].round(2), 
            hovertemplate='Time: %{x}<br>Depth: %{y} dbar<br>Temp: %{text}°C<extra></extra>',
            name='Temperature'
        ))
        
        fig.update_layout(
            title=f'Temperature Depth-Time Curtain Plot - {region_name}',
            xaxis_title='Time',
            yaxis_title='Pressure (dbar)', 
            yaxis=dict(autorange='reversed'), 
            height=600
        )
        return fig
    else:
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        sample_df = df.sample(min(1000, len(df))) if len(df) > 1000 else df
        
        scatter = ax.scatter(sample_df['time'], sample_df['PRES'], 
                           c=sample_df['TEMP'], cmap='RdYlBu_r', alpha=0.6, s=20)
        ax.set_xlabel('Time')
        ax.set_ylabel('Pressure (dbar)')
        ax.set_title(f'Temperature Depth-Time Curtain Plot - {region_name}')
        ax.invert_yaxis()
        
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Temperature (°C)', rotation=270, labelpad=15)
        plt.tight_layout()
        return fig

def create_ts_diagram(df, region_name):
    """Create Temperature-Salinity diagram"""
    if len(df) == 0: 
        return None
    
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    scatter = ax.scatter(df['PSAL'], df['TEMP'], c=df['PRES'], 
                        cmap='viridis_r', alpha=0.6, s=20)
    ax.set_xlabel('Salinity (PSU)')
    ax.set_ylabel('Temperature (°C)')
    ax.set_title(f'Temperature-Salinity Diagram\n{region_name}')
    ax.grid(True, alpha=0.3)
    
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Pressure (dbar)', rotation=270, labelpad=15)
    plt.tight_layout()
    return fig

def create_surface_anomaly_map(df, region_name):
    """Create surface anomaly map"""
    if len(df) == 0: 
        return None
    
    surface_data = df[df['PRES'] <= 10].copy()
    if len(surface_data) == 0: 
        st.warning("No surface data available for mapping")
        return None
    
    if PLOTLY_AVAILABLE:
        fig = px.scatter_mapbox(
            surface_data, 
            lat='latitude', 
            lon='longitude', 
            color='TEMP',
            size_max=15, 
            zoom=3, 
            mapbox_style="open-street-map",
            color_continuous_scale='RdYlBu_r', 
            title=f'Sea Surface Temperature Anomaly - {region_name}',
            labels={'TEMP': 'Temperature (°C)'}, 
            hover_data=['PSAL', 'PRES']
        )
        fig.update_layout(height=600)
        return fig
    else:
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        scatter = ax.scatter(surface_data['longitude'], surface_data['latitude'], 
                           c=surface_data['TEMP'], cmap='RdYlBu_r', alpha=0.7, s=30)
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.set_title(f'Sea Surface Temperature - {region_name}')
        ax.grid(True, alpha=0.3)
        
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Temperature (°C)', rotation=270, labelpad=15)
        plt.tight_layout()
        return fig

def create_histograms(df, region_name, variables):
    """Create histograms for selected variables"""
    if len(df) == 0: 
        return None
    
    plot_vars = []
    if 'Temperature' in variables: 
        plot_vars.append(('TEMP', 'Temperature (°C)', 'red'))
    if 'Salinity' in variables: 
        plot_vars.append(('PSAL', 'Salinity (PSU)', 'blue'))
    if 'Pressure' in variables: 
        plot_vars.append(('PRES', 'Pressure (dbar)', 'green'))
    
    n_plots = len(plot_vars)
    if n_plots == 0: 
        return None
    
    fig, axes = plt.subplots(1, n_plots, figsize=(5*n_plots, 6))
    if n_plots == 1: 
        axes = [axes]
    
    for i, (var, label, color) in enumerate(plot_vars):
        if var in df.columns:
            data = df[var].dropna()
            axes[i].hist(data, bins=50, alpha=0.7, color=color, density=True)
            axes[i].set_xlabel(label)
            axes[i].set_ylabel('Density')
            axes[i].set_title(f'{label} Distribution\n{region_name}')
            axes[i].grid(True, alpha=0.3)
            
            mean_val = data.mean()
            axes[i].axvline(mean_val, color='black', linestyle='--', alpha=0.8, 
                           label=f'Mean: {mean_val:.2f}')
            axes[i].legend()
    
    plt.tight_layout()
    return fig

def create_ocean_map(df, region_name, variables, bbox):
    """Create interactive Folium map"""
    center_lat = (bbox["lat_min"] + bbox["lat_max"]) / 2
    center_lon = (bbox["lon_min"] + bbox["lon_max"]) / 2
    
    m = folium.Map(
        location=[center_lat, center_lon], 
        zoom_start=4,
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri &mdash; Source: Esri, Maxar, Earthstar Geographics"
    )
    
    if len(df) == 0: 
        st.warning("No data to display on map")
        return m
    
    # Add region rectangle
    folium.Rectangle(
        bounds=[[bbox["lat_min"], bbox["lon_min"]], [bbox["lat_max"], bbox["lon_max"]]],
        color="yellow", 
        fill=False, 
        weight=2, 
        popup=f"Search Region: {region_name}"
    ).add_to(m)
    
    # Add markers
    marker_cluster = MarkerCluster().add_to(m)
    sample_size = min(200, len(df))
    df_sample = df.sample(n=sample_size) if len(df) > sample_size else df
    
    for idx, row in df_sample.iterrows():
        float_status = "Active"
        if 'DATA_MODE' in df.columns:
            data_mode = str(row['DATA_MODE'])
            if data_mode in ['D', 'A']: 
                float_status = "Active"
            elif data_mode in ['R']: 
                float_status = "Inactive"
            else: 
                float_status = "Unknown"
        
        popup_content = f"""
        <b>Argo Float Data</b><br>
        <b>Status:</b> {float_status}<br>
        <b>Lat:</b> {row['latitude']:.3f}<br>
        <b>Lon:</b> {row['longitude']:.3f}<br>
        """
        
        if 'PLATFORM_NUMBER' in df.columns: 
            popup_content += f"<b>Float ID:</b> {row['PLATFORM_NUMBER']}<br>"
        if 'TEMP' in df.columns: 
            popup_content += f"<b>Temperature:</b> {row['TEMP']:.2f}°C<br>"
        if 'PSAL' in df.columns: 
            popup_content += f"<b>Salinity:</b> {row['PSAL']:.2f} PSU<br>"
        if 'PRES' in df.columns: 
            popup_content += f"<b>Pressure:</b> {row['PRES']:.1f} dbar<br>"
        
        color = 'green' if float_status=="Active" else ('red' if float_status=="Inactive" else 'gray')
        
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']], 
            radius=5, 
            popup=popup_content,
            color='white', 
            fillColor=color, 
            fillOpacity=0.7, 
            weight=1
        ).add_to(marker_cluster)
    
    # Add temperature heatmap if available
    if 'TEMP' in df.columns and len(df) > 10:
        heat_data = [[row['latitude'], row['longitude'], row['TEMP']] 
                    for idx, row in df.iterrows() if not pd.isna(row['TEMP'])]
        HeatMap(heat_data, name='Temperature Heat Map', radius=15, blur=10, show=False).add_to(m)
    
    folium.LayerControl().add_to(m)
    
    # Add legend
    legend_html = f"""
    <div style='position: fixed; bottom: 30px; left: 30px; width: 200px; z-index:9999; 
                 font-size:12px; background:white; padding:15px; border:2px solid grey; 
                 border-radius: 5px;'>
        <b>Ocean Data Legend</b><br>
        <b>Region:</b> {region_name}<br>
        <b>Data Points:</b> {len(df):,}<br><br>
        <b>Float Status:</b><br>
        <span style='color: green;'>● Active Floats</span><br>
        <span style='color: red;'>● Inactive Floats</span><br>
        <span style='color: gray;'>● Unknown Status</span><br><br>
        <b>Variables:</b> {', '.join(variables) if variables else 'All'}<br>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
    
    return m

# --------------------------- Main App ---------------------------
def main():
    # Header
    st.markdown('<h1 class="main-header">🌊 Ocean Data Explorer Chatbot</h1>', unsafe_allow_html=True)
    
    # Main chatbot interface
    st.markdown("### 🤖 Ask me about ocean data!")
    st.markdown("*Example: 'Show me temperature in the Indian Ocean from 2024-06-01 to 2024-06-15'*")
    
    # Chatbot input
    user_query = st.text_area(
        "💬 Enter your ocean data query:",
        placeholder="e.g., 'Show temperature and salinity in the North Atlantic in June 2024'",
        height=100,
        key="chatbot_query"
    )
    
    # AI assistance for ocean data queries
    if user_query:
        if st.button("💬 Ask AI About Ocean Data", help="Get AI assistance about your query"):
            groq_client = initialize_groq()
            index, model = initialize_pinecone()
            
            if groq_client:
                with st.spinner("🤖 AI is thinking..."):
                    context = get_relevant_context(user_query, index, model) if index and model else ""
                    ai_response = process_detailed_ai_assistant(user_query, groq_client, context)
                
                if ai_response:
                    st.markdown("### 🤖 AI Ocean Data Assistant")
                    with st.expander("💡 AI Insights & Guidance", expanded=True):
                        st.markdown(ai_response)
            else:
                st.info("🤖 AI assistance requires Groq API key configuration")
    
    # Sidebar for visualization options only
    st.sidebar.title("🎨 Visualization Options")
    st.sidebar.markdown("---")
    
    viz_type = st.sidebar.radio(
        "Choose what to display:",
        ["Graphs Only", "Map Only", "Both Graphs and Map"],
        index=2
    )
    
    # Parse query when user enters text
    if user_query:
        with st.expander("🔍 Parsed Query Details", expanded=False):
            region_name, parsed_start_date, parsed_end_date, variables = parse_query(user_query)
            
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**Region:** {region_name}")
                st.info(f"**Variables:** {', '.join(variables)}")
            with col2:
                st.info(f"**Start Date:** {parsed_start_date}")
                st.info(f"**End Date:** {parsed_end_date}")
        
        # Convert parsed dates to date objects
        try:
            start_date = datetime.datetime.strptime(parsed_start_date, "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(parsed_end_date, "%Y-%m-%d").date()
        except:
            start_date = date(2024, 6, 1)
            end_date = date(2024, 6, 15)
    else:
        # Default values when no query
        region_name = "Indian Ocean"
        variables = ["Temperature", "Salinity", "Pressure"]
        start_date = date(2024, 6, 1)
        end_date = date(2024, 6, 15)
    
    # Fetch data button
    fetch_button = st.button("🔍 Fetch Ocean Data", type="primary")
    
    # Main content area
    if fetch_button:
        bbox = REGIONS[region_name]
        
        # Show educational content while fetching data
        with st.spinner(f"🌊 Fetching ocean data for {region_name}..."):
            # Display educational content during data fetching
            if GROQ_AVAILABLE and PINECONE_AVAILABLE:
                groq_client = initialize_groq()
                index, model = initialize_pinecone()
                
                if groq_client and index and model:
                    # Create educational query about the region
                    educational_query = f"Tell me interesting facts and characteristics about the {region_name} region while data is being fetched"
                    
                    # Get relevant context from vector database
                    context = get_relevant_context(educational_query, index, model)
                    
                    # Generate educational content
                    educational_content = process_query_with_groq(educational_query, groq_client, context)
                    
                    if educational_content:
                        st.markdown("### 🌊 While We Fetch Your Data...")
                        st.info("Here's some interesting information about this ocean region:")
                        st.markdown(educational_content)
                        st.markdown("---")
        
            # Fetch data
            df = fetch_argo_data(region_name, start_date, end_date, bbox)
        
        if len(df) == 0:
            st.error("No data found for the selected parameters. Please try different settings.")
            return
        
        # Display data summary
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🌊 Data Points", f"{len(df):,}")
        
        with col2:
            if 'TEMP' in df.columns:
                avg_temp = df['TEMP'].mean()
                st.metric("🌡️ Avg Temperature", f"{avg_temp:.1f}°C")
        
        with col3:
            if 'PSAL' in df.columns:
                avg_sal = df['PSAL'].mean()
                st.metric("🧂 Avg Salinity", f"{avg_sal:.1f} PSU")
        
        with col4:
            if 'PRES' in df.columns:
                max_depth = df['PRES'].max()
                st.metric("🏊 Max Depth", f"{max_depth:.0f} dbar")
        
        st.markdown("---")
        
        # Generate visualizations based on user choice
        if viz_type in ["Graphs Only", "Both Graphs and Map"]:
            st.header("📊 Data Visualizations")
            
            # Vertical Profile
            with st.expander("🌡️ Vertical Profiles", expanded=True):
                fig = create_vertical_profile(df, region_name)
                if fig:
                    st.pyplot(fig)
                else:
                    st.warning("No data available for vertical profiles")
            
            # Depth-Time Curtain
            with st.expander("⏰ Depth-Time Curtain Plot", expanded=False):
                fig = create_depth_time_curtain(df, region_name)
                if fig:
                    if PLOTLY_AVAILABLE:
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.pyplot(fig)
                else:
                    st.warning("No time data available for curtain plot")
            
            # T-S Diagram
            with st.expander("🔬 Temperature-Salinity Diagram", expanded=False):
                fig = create_ts_diagram(df, region_name)
                if fig:
                    st.pyplot(fig)
                else:
                    st.warning("No data available for T-S diagram")
            
            # Surface Anomaly Map
            with st.expander("🗺️ Surface Temperature Map", expanded=False):
                fig = create_surface_anomaly_map(df, region_name)
                if fig:
                    if PLOTLY_AVAILABLE:
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.pyplot(fig)
                else:
                    st.warning("No surface data available")
            
            # Histograms
            with st.expander("📊 Variable Distributions", expanded=False):
                fig = create_histograms(df, region_name, variables)
                if fig:
                    st.pyplot(fig)
                else:
                    st.warning("No data available for histograms")
        
        if viz_type in ["Map Only", "Both Graphs and Map"]:
            st.header("🗺️ Interactive Ocean Map")
            
            # Create and display map
            ocean_map = create_ocean_map(df, region_name, variables, bbox)
            st_folium.folium_static(ocean_map, width=1200, height=600)
            
            # Download option for map
            if st.button("💾 Save Map"):
                map_filename = f"ocean_map_{region_name.lower().replace(' ', '_')}_{start_date}.html"
                ocean_map.save(map_filename)
                st.success(f"Map saved as {map_filename}")
        
        # Data download and preview option - WITH SUMMARY STATISTICS
        st.markdown("---")
        st.subheader("📋 Data Table & Download")
        
        # Show data preview and statistics side by side
        col1, col2 = st.columns(2)
        
        with col1:
            with st.expander("📊 View Data Table", expanded=False):
                st.dataframe(df, use_container_width=True, height=400)
                st.info(f"Showing {len(df):,} records from {region_name}")
        
        with col2:
            with st.expander("📈 Summary Statistics", expanded=False):
                # Generate summary statistics for numeric columns
                numeric_cols = ['TEMP', 'PSAL', 'PRES', 'latitude', 'longitude']
                available_cols = [col for col in numeric_cols if col in df.columns]
                
                if available_cols:
                    summary_stats = df[available_cols].describe()
                    st.dataframe(summary_stats, use_container_width=True, height=400)
                    
                    # Download summary statistics
                    summary_csv = summary_stats.to_csv()
                    st.download_button(
                        label="📊 Download Statistics CSV",
                        data=summary_csv,
                        file_name=f"ocean_stats_{region_name.lower().replace(' ', '_')}_{start_date}_{end_date}.csv",
                        mime="text/csv",
                        key="stats_download"
                    )
                else:
                    st.warning("No numeric data available for statistics")
        
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Full Data CSV",
            data=csv_data,
            file_name=f"ocean_data_{region_name.lower().replace(' ', '_')}_{start_date}_{end_date}.csv",
            mime="text/csv"
        )
    
    else:
        # Welcome message and chatbot instructions
        st.info("👋 Welcome to Ocean Data Explorer Chatbot! Ask me anything about ocean data using natural language.")
        
        # Instructions and examples
        st.markdown("""
        ### 🤖 How to Use the Chatbot:
        
        Simply type your question in natural language! Here are some examples:
        
        #### 📝 Example Queries:
        - *"Show me temperature in the Indian Ocean from 2024-06-01 to 2024-06-15"*
        - *"Display salinity data for North Atlantic in June 2024"*  
        - *"I want to see temperature and pressure in the Pacific Ocean"*
        - *"Show all variables for Southern Ocean in July 2024"*
        - *"Temperature data in South Atlantic from 2024-05-01 to 2024-05-30"*
        
        #### 🌍 Supported Regions:
        - Indian Ocean, North Atlantic, South Atlantic
        - North Pacific, South Pacific, Southern Ocean
        
        #### 📊 Available Variables:
        - **Temperature** (°C) - Ocean water temperature
        - **Salinity** (PSU) - Salt content of seawater  
        - **Pressure** (dbar) - Water pressure/depth measurements
        
        #### 📅 Date Formats:
        - Specific dates: `2024-06-01` or `2024-06-01 to 2024-06-15`
        - Month/Year: `June 2024` or `July 2023`
        
        ### 🎨 Visualization Options:
        Use the sidebar to choose what you want to see:
        - **Graphs Only**: All analytical plots and charts
        - **Map Only**: Interactive map with float locations  
        - **Both**: Complete visualization suite
        
        ### 🔍 Available Features:
        - **Vertical Profiles**: Temperature and salinity vs depth
        - **Depth-Time Curtains**: Temperature evolution over time and depth
        - **T-S Diagrams**: Water mass characteristic analysis
        - **Surface Maps**: Sea surface temperature visualization
        - **Interactive Maps**: Argo float locations with detailed information
        - **Data Export**: Download processed data as CSV files
        """)

if __name__ == "__main__":
    main()
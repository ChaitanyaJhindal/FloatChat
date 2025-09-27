"""
Enhanced Pinecone Population Script
Adds ArgoPy documentation + Query Understanding content for Groq integration
"""

from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

def populate_enhanced_argopy_docs():
    """Populate Pinecone with ArgoPy docs + query understanding content"""
    
    # Initialize Pinecone
    api_key = os.getenv("PINECONE_API_KEY")
    
    from pinecone import Pinecone, ServerlessSpec
    pc = Pinecone(api_key=api_key)
    
    # Load model
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L12-v2')
    
    # Connect to index
    index = pc.Index("floatchat")
    
    # Enhanced documentation with query understanding content
    enhanced_docs = [
        # Original ArgoPy docs (keeping existing ones)
        {
            "title": "ArgoPy Data Fetching Basics",
            "content": "ArgoPy DataFetcher is the main class for accessing Argo float data. Use ArgoDataFetcher(src='argovis') for real-time data or src='gdac' for quality-controlled delayed mode data. Basic usage: argo = ArgoDataFetcher(src='argovis')",
            "category": "technical"
        },
        {
            "title": "Region Method Parameters",
            "content": "The region method requires [lon_min, lon_max, lat_min, lat_max, pres_min, pres_max, start_date, end_date]. Longitude: -180 to 180, Latitude: -90 to 90, Pressure: 0 to 2000 dbar typically, Dates: YYYY-MM-DD format.",
            "category": "technical"
        },
        
        # NEW: Query Understanding and Natural Language Processing
        {
            "title": "Understanding Temperature Queries",
            "content": "When users ask about temperature: 'temperature', 'temp', 'water temperature', 'sea surface temperature', 'SST' all refer to TEMP variable. Common queries: 'show temperature in Pacific', 'temp data for June', 'water temperature trends'. Default to surface temperature (0-10 dbar) unless depth specified.",
            "category": "query_understanding"
        },
        {
            "title": "Understanding Salinity Queries", 
            "content": "Salinity queries include: 'salinity', 'salt content', 'PSU', 'practical salinity', 'saltiness'. Users might ask 'salt levels in ocean', 'salinity variations', 'how salty is water'. Maps to PSAL variable. Typical range: 30-37 PSU in open ocean.",
            "category": "query_understanding"
        },
        {
            "title": "Understanding Geographic Queries",
            "content": "Geographic terms mapping: 'Pacific' -> North Pacific or South Pacific, 'Atlantic' -> North Atlantic, 'Indian Ocean', 'Antarctic' -> Southern Ocean, 'Arctic Ocean' -> use custom coordinates. Users may say 'near Japan' (North Pacific), 'Mediterranean' (custom region), 'equator' (latitude near 0).",
            "category": "query_understanding"
        },
        {
            "title": "Understanding Time Period Queries",
            "content": "Time expressions: 'last month' -> previous month dates, 'June 2024' -> 2024-06-01 to 2024-06-30, 'summer 2023' -> June-August 2023, 'recent data' -> last 30 days, 'this year' -> current year Jan-Dec. Always convert to YYYY-MM-DD format.",
            "category": "query_understanding"
        },
        {
            "title": "Handling Vague Location Queries",
            "content": "When users give vague locations: 'somewhere in Pacific' -> suggest North Pacific default, 'near coast' -> ask for specific region, 'tropical waters' -> equatorial regions, 'cold waters' -> higher latitudes, 'deep ocean' -> far from coast. Always suggest specific lat/lon ranges.",
            "category": "query_reframing"
        },
        {
            "title": "Handling Incomplete Date Queries",
            "content": "Incomplete dates: 'June' -> ask which year, suggest current/previous year, 'summer' -> ask specific year, suggest Jun-Aug, '2024' -> ask which months, suggest recent months, 'recently' -> suggest last 30-90 days. Provide default date ranges when possible.",
            "category": "query_reframing"
        },
        {
            "title": "Reframing Scientific Questions",
            "content": "Scientific queries to reframe: 'climate change effects' -> 'temperature trends over time', 'ocean warming' -> 'temperature variations by region and time', 'El Niño impact' -> 'Pacific temperature and salinity anomalies', 'current patterns' -> 'temperature and salinity gradients'. Focus on available Argo variables.",
            "category": "query_reframing"
        },
        {
            "title": "Common Query Mistakes and Fixes",
            "content": "Common mistakes: 'ocean depth' -> use 'pressure levels', 'current speed' -> not available in Argo data, 'wave height' -> not in Argo, suggest pressure/temperature, 'fish populations' -> not oceanographic data, suggest water properties, 'pollution levels' -> not available, suggest temperature/salinity patterns.",
            "category": "query_reframing"
        },
        {
            "title": "Improving Ambiguous Queries",
            "content": "Ambiguous query improvements: 'show me data' -> ask for variable, region, time, 'ocean information' -> specify temperature/salinity/pressure, 'water conditions' -> suggest temperature and salinity, 'marine data' -> focus on physical oceanographic variables available in Argo.",
            "category": "query_reframing"
        },
        {
            "title": "Beginner-Friendly Query Suggestions",
            "content": "For beginners suggest: 'Start with sea surface temperature in [region] for [recent month]', 'Try salinity patterns in major ocean basins', 'Compare temperature at different depths', 'Explore seasonal variations in your region of interest'. Provide complete example queries.",
            "category": "query_reframing"
        },
        {
            "title": "Advanced Query Enhancement",
            "content": "Advanced users: suggest specific pressure ranges, multiple regions for comparison, time series analysis, seasonal comparisons, vertical profile analysis, water mass identification using T-S diagrams, regional oceanographic phenomena, multi-variable correlations.",
            "category": "query_reframing"
        },
        {
            "title": "Regional Ocean Knowledge",
            "content": "Regional expertise: North Atlantic (Gulf Stream, deep water formation), Pacific (ENSO, PDO, typhoon regions), Indian Ocean (monsoons, IOD), Southern Ocean (circumpolar current, sea ice), Arctic (ice coverage, warming trends). Use this knowledge to enhance user queries with relevant oceanographic context.",
            "category": "oceanography_knowledge"
        },
        {
            "title": "Seasonal Pattern Suggestions",
            "content": "Seasonal oceanography: Summer (stratification, warming), Winter (mixing, cooling), Spring (bloom conditions), Fall (transition periods). Suggest seasonal comparisons, multi-year trends, climate indices correlation, regional seasonal differences. Help users understand when to expect interesting patterns.",
            "category": "oceanography_knowledge"
        },
        {
            "title": "Data Quality and Limitations Guidance",
            "content": "Guide users on data expectations: Real-time data may have quality issues, delayed mode is better for research, sparse data in polar regions, more data in shipping lanes, recent years have better coverage, some regions have seasonal gaps. Set realistic expectations for data availability.",
            "category": "data_guidance"
        },
        
        # Error handling and troubleshooting (enhanced)
        {
            "title": "Smart Error Recovery Strategies",
            "content": "When data fetching fails: 1) Suggest reducing geographic area, 2) Shorten time period, 3) Try different data source, 4) Check if region has Argo coverage, 5) Verify date format and range, 6) Suggest alternative regions with better data coverage, 7) Explain seasonal data availability patterns.",
            "category": "error_handling"
        }
    ]
    
    print("🌊 Populating Enhanced ArgoPy + Query Understanding Documentation...")
    
    vectors_to_upsert = []
    
    for doc in enhanced_docs:
        # Generate embedding
        embedding = model.encode(doc["content"]).tolist()
        
        # Adjust to 512 dimensions
        if len(embedding) > 512:
            embedding = embedding[:512]
        elif len(embedding) < 512:
            embedding.extend([0.0] * (512 - len(embedding)))
        
        # Prepare for upsert
        vectors_to_upsert.append({
            "id": str(uuid.uuid4()),
            "values": embedding,
            "metadata": {
                "title": doc["title"],
                "content": doc["content"],
                "category": doc["category"],
                "topic": "argopy_enhanced"
            }
        })
    
    # Upsert in batches
    batch_size = 10
    for i in range(0, len(vectors_to_upsert), batch_size):
        batch = vectors_to_upsert[i:i + batch_size]
        index.upsert(vectors=batch)
        print(f"✅ Uploaded batch {i//batch_size + 1}/{(len(vectors_to_upsert)-1)//batch_size + 1}")
    
    print(f"🎉 Successfully populated {len(enhanced_docs)} enhanced documentation entries!")
    
    # Test various query types
    test_queries = [
        "show me temperature data",
        "Pacific Ocean salinity",
        "what is the temperature in tropical waters",
        "I want to see ocean data for summer",
        "show me marine conditions"
    ]
    
    print("\n🔍 Testing enhanced query understanding...")
    for query in test_queries:
        test_embedding = model.encode(query).tolist()
        
        if len(test_embedding) > 512:
            test_embedding = test_embedding[:512]
        elif len(test_embedding) < 512:
            test_embedding.extend([0.0] * (512 - len(test_embedding)))
        
        results = index.query(
            vector=test_embedding,
            top_k=2,
            include_metadata=True
        )
        
        print(f"\nQuery: '{query}'")
        for match in results['matches']:
            if match['score'] > 0.5:
                print(f"  - {match['metadata']['title']} (Score: {match['score']:.3f})")

if __name__ == "__main__":
    populate_enhanced_argopy_docs()
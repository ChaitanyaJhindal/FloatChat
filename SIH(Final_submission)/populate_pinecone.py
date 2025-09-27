"""
Populate Pinecone Vector Database with ArgoPy Documentation
Run this script once to populate your floatchat index with ArgoPy documentation
"""

import pinecone
from sentence_transformers import SentenceTransformer
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

def populate_argopy_docs():
    """Populate the Pinecone index with ArgoPy documentation"""
    
    # Initialize Pinecone with your configuration
    api_key = os.getenv("PINECONE_API_KEY")
    
    from pinecone import Pinecone, ServerlessSpec
    pc = Pinecone(api_key=api_key)
    
    # Load sentence transformer
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L12-v2')
    
    # Connect to your index
    index = pc.Index("floatchat")
    
    # ArgoPy documentation chunks
    argopy_docs = [
        {
            "title": "ArgoPy Data Fetching Basics",
            "content": "ArgoPy DataFetcher is the main class for accessing Argo float data. Use ArgoDataFetcher(src='argovis') for real-time data or src='gdac' for quality-controlled delayed mode data. Basic usage: argo = ArgoDataFetcher(src='argovis')"
        },
        {
            "title": "Region Method Parameters",
            "content": "The region method requires [lon_min, lon_max, lat_min, lat_max, pres_min, pres_max, start_date, end_date]. Longitude: -180 to 180, Latitude: -90 to 90, Pressure: 0 to 2000 dbar typically, Dates: YYYY-MM-DD format."
        },
        {
            "title": "Common Data Fetching Errors",
            "content": "Connection timeouts often occur with large data requests. Solution: reduce date range or geographic area. Empty datasets happen when no floats exist in specified region/time. Check Argo float coverage maps first."
        },
        {
            "title": "Internet Connection Issues",
            "content": "ArgoPy requires stable internet connection to access remote data servers. If getting connection errors, check: 1) Internet connectivity, 2) Server status at argovis.colorado.edu, 3) Try different data source with src='erddap'"
        },
        {
            "title": "Date Range Problems",
            "content": "Invalid date ranges cause errors. Ensure: start_date < end_date, dates not in future, dates in YYYY-MM-DD format. Argo data availability starts from ~2000. Recent data may have delays."
        },
        {
            "title": "Geographic Coordinate Errors",
            "content": "Longitude must be -180 to 180 degrees. Latitude must be -90 to 90 degrees. Invalid coordinates cause data fetching failures. Use decimal degrees, not degrees/minutes/seconds."
        },
        {
            "title": "Empty Dataset Troubleshooting",
            "content": "No data returned can mean: 1) No Argo floats in specified region/time, 2) Network issues, 3) Server problems. Try: expand geographic area, check different time period, use Argo float coverage maps."
        },
        {
            "title": "Data Source Options",
            "content": "ArgoPy supports multiple sources: 'argovis' (real-time, Colorado), 'erddap' (IFREMER ERDDAP), 'gdac' (delayed mode, quality controlled). Each has different data availability and update frequencies."
        },
        {
            "title": "Memory and Performance Issues",
            "content": "Large datasets can cause memory errors. Solutions: 1) Reduce spatial/temporal scope, 2) Process data in chunks, 3) Use pressure limits to reduce vertical resolution, 4) Sample subset of floats."
        },
        {
            "title": "Column Name Variations",
            "content": "Argo data column names vary: Temperature: TEMP, PTEMP; Salinity: PSAL, SAL; Pressure: PRES; Coordinates: LATITUDE/latitude, LONGITUDE/longitude. Always check df.columns after fetching."
        },
        {
            "title": "Data Quality Flags",
            "content": "Argo data includes quality flags: DATA_MODE shows R (real-time) vs D (delayed). TEMP_QC, PSAL_QC show data quality (1=good, 2=probably good, 3=probably bad, 4=bad, 9=missing)."
        },
        {
            "title": "Timeout Handling",
            "content": "Server timeouts with large requests. Solutions: 1) Reduce date range (try 1 month), 2) Smaller geographic box, 3) Limit pressure range 0-100 dbar for surface, 4) Use different src parameter."
        },
        {
            "title": "Missing Data Handling",
            "content": "Argo profiles often have missing values (NaN). Use pandas dropna() to remove incomplete records, or fillna() for interpolation. Check data coverage before analysis."
        },
        {
            "title": "Float Platform Information",
            "content": "Each Argo float has PLATFORM_NUMBER (unique ID) and CYCLE_NUMBER (profile sequence). Use these to track individual float trajectories and profile sequences."
        },
        {
            "title": "Pressure vs Depth",
            "content": "Argo measures pressure (PRES in dbar), not depth. Approximate conversion: depth(m) ≈ pressure(dbar) × 1.02. For precise depth, use gsw.z_from_p() function."
        },
        {
            "title": "Data Processing Pipeline",
            "content": "Typical workflow: 1) Fetch with ArgoDataFetcher, 2) Convert to pandas with .to_dataframe(), 3) Handle missing values, 4) Quality control filtering, 5) Analysis/visualization."
        },
        {
            "title": "Server Status and Alternatives",
            "content": "If argovis fails, try: 1) Different src='erddap' or 'gdac', 2) Check server status, 3) Reduce request size, 4) Wait and retry (servers may be temporarily busy)."
        },
        {
            "title": "Best Practices for Data Requests",
            "content": "For reliable data fetching: 1) Start with small region/time, 2) Check data availability first, 3) Handle exceptions gracefully, 4) Cache results, 5) Validate coordinates before request."
        }
    ]
    
    # Process and upload documents
    print("🌊 Populating ArgoPy documentation in Pinecone...")
    
    vectors_to_upsert = []
    
    for doc in argopy_docs:
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
                "topic": "argopy"
            }
        })
    
    # Upsert in batches
    batch_size = 10
    for i in range(0, len(vectors_to_upsert), batch_size):
        batch = vectors_to_upsert[i:i + batch_size]
        index.upsert(vectors=batch)
        print(f"✅ Uploaded batch {i//batch_size + 1}/{(len(vectors_to_upsert)-1)//batch_size + 1}")
    
    print(f"🎉 Successfully populated {len(argopy_docs)} ArgoPy documentation entries!")
    
    # Test query
    print("\n🔍 Testing documentation query...")
    test_query = "connection timeout error"
    test_embedding = model.encode(test_query).tolist()
    
    if len(test_embedding) > 512:
        test_embedding = test_embedding[:512]
    elif len(test_embedding) < 512:
        test_embedding.extend([0.0] * (512 - len(test_embedding)))
    
    results = index.query(
        vector=test_embedding,
        top_k=3,
        include_metadata=True
    )
    
    print(f"Found {len(results['matches'])} relevant documents:")
    for match in results['matches']:
        print(f"- {match['metadata']['title']} (Score: {match['score']:.3f})")

if __name__ == "__main__":
    populate_argopy_docs()
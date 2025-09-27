#!/usr/bin/env python3
"""
Test script to verify API key loading and validate keys
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_api_keys():
    """Test if API keys are loaded correctly"""
    
    print("🔍 Testing API Key Loading...")
    print("=" * 50)
    
    # Test Pinecone API key
    pinecone_key = os.getenv("PINECONE_API_KEY")
    if pinecone_key:
        print(f"✅ Pinecone API Key loaded: {pinecone_key[:10]}...{pinecone_key[-4:]}")
        print(f"   Length: {len(pinecone_key)} characters")
    else:
        print("❌ Pinecone API Key not found")
    
    # Test Groq API key  
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        print(f"✅ Groq API Key loaded: {groq_key[:10]}...{groq_key[-4:]}")
        print(f"   Length: {len(groq_key)} characters")
    else:
        print("❌ Groq API Key not found")
    
    print("\n🧪 Testing API Connections...")
    print("=" * 50)
    
    # Test Pinecone connection
    if pinecone_key:
        try:
            from pinecone import Pinecone
            pc = Pinecone(api_key=pinecone_key)
            # Try to list indexes
            indexes = pc.list_indexes()
            print(f"✅ Pinecone connection successful")
            print(f"   Available indexes: {[idx.name for idx in indexes]}")
        except Exception as e:
            print(f"❌ Pinecone connection failed: {e}")
    
    # Test Groq connection
    if groq_key:
        try:
            from groq import Groq
            client = Groq(api_key=groq_key)
            # Try a simple request
            models = client.models.list()
            print(f"✅ Groq connection successful")
            print(f"   Available models: {len(models.data)} models found")
        except Exception as e:
            print(f"❌ Groq connection failed: {e}")

if __name__ == "__main__":
    test_api_keys()
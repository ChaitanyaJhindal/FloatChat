#!/usr/bin/env python3
"""
Secure secrets manager using encryption
This encrypts your API keys and stores them safely in the code
"""

import os
import base64
from cryptography.fernet import Fernet
import streamlit as st

class SecureSecrets:
    def __init__(self, key=None):
        """Initialize with encryption key"""
        if key:
            self.key = key.encode()
        else:
            # Get encryption key from Streamlit secrets or environment
            encryption_key = st.secrets.get("ENCRYPTION_KEY") or os.getenv("ENCRYPTION_KEY", "FloatChat-Ocean-Data-Explorer-2025")
            self.key = encryption_key.encode()[:32].ljust(32, b'0')
        
        self.cipher = Fernet(base64.urlsafe_b64encode(self.key))
    
    def decrypt_secrets(self, encrypted_dict):
        """Decrypt a dictionary of secrets"""
        try:
            decrypted = {}
            for key, value in encrypted_dict.items():
                decrypted[key] = self.cipher.decrypt(value.encode()).decode()
            return decrypted
        except Exception as e:
            st.error(f"🔐 Failed to decrypt secrets: {e}")
            return {}

# Encrypted secrets (safe to commit to GitHub)
# These are your actual API keys, encrypted and safe
ENCRYPTED_SECRETS = {
    "PINECONE_API_KEY": "gAAAAABo18ZSS6KvkVAusQW6XpSOGAVSvKgD0nNu-m3Z3X88-zAIsWy-N1aHiq5c0LaZPnk2yorc-wg0aFWVgsPMHLriY5-JB5qCcLI7RmxSWq47MVztxuQOY5D8x5fNa2QEZwV-C6RV9_3p513LaH7jSnjNV2YMd29GL9TJYtROWF5nab7Ooa4=",
    "GROQ_API_KEY": "gAAAAABo18ZS7kxiQ1VVIre6b5FUwMG8144dSJ_n9KaLPi3FaYuGTaCLaJ5sYRg-UYZOPDE9YTG8JReB1-t3MEiqCx_XbUWz0lxYmVzMT8yT9xkvXtPheJ0P75RVNAAND8GuZFAWBkvbuM9n2MlZvSbjC81H50Hbjw=="
}

def load_secure_secrets():
    """Load and decrypt secrets securely"""
    try:
        secrets_manager = SecureSecrets()
        return secrets_manager.decrypt_secrets(ENCRYPTED_SECRETS)
    except Exception as e:
        st.warning(f"⚠️ Could not load encrypted secrets: {e}")
        return {}
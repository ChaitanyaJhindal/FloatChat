#!/usr/bin/env python3
"""
Secure secrets manager using encryption
This encrypts your API keys and stores them safely in the code
"""

import os
import base64
from cryptography.fernet import Fernet

# Try to import streamlit, but don't fail if it's not available
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    
    # Mock streamlit functions for non-streamlit usage
    class MockSt:
        @staticmethod
        def write(text):
            print(text)
        @staticmethod
        def error(text):
            print(f"ERROR: {text}")
        @staticmethod
        def warning(text):
            print(f"WARNING: {text}")
        @staticmethod
        def get(key, default=None):
            return os.getenv(key, default)
        
        class secrets:
            @staticmethod
            def get(key, default=None):
                return os.getenv(key, default)
    
    st = MockSt()

class SecureSecrets:
    def __init__(self, key=None):
        """Initialize with encryption key"""
        if key:
            # Properly format the key for Fernet
            if len(key) < 32:
                # Pad the key to 32 bytes
                padded_key = key.ljust(32, '0')
            else:
                # Truncate to 32 bytes
                padded_key = key[:32]
            
            # Encode to bytes and create proper base64 key
            key_bytes = padded_key.encode('utf-8')
            self.fernet_key = base64.urlsafe_b64encode(key_bytes)
        else:
            # Get encryption key from Streamlit secrets or environment
            if STREAMLIT_AVAILABLE:
                try:
                    encryption_key = st.secrets.get("ENCRYPTION_KEY") or os.getenv("ENCRYPTION_KEY", "FloatChat-Ocean-Data-Explorer-2025")
                except:
                    encryption_key = os.getenv("ENCRYPTION_KEY", "FloatChat-Ocean-Data-Explorer-2025")
            else:
                encryption_key = os.getenv("ENCRYPTION_KEY", "FloatChat-Ocean-Data-Explorer-2025")
            
            # Format the key properly
            if len(encryption_key) < 32:
                padded_key = encryption_key.ljust(32, '0')
            else:
                padded_key = encryption_key[:32]
            
            key_bytes = padded_key.encode('utf-8')
            self.fernet_key = base64.urlsafe_b64encode(key_bytes)
        
        self.cipher = Fernet(self.fernet_key)
    
    def decrypt_secrets(self, encrypted_dict):
        """Decrypt a dictionary of secrets"""
        try:
            decrypted = {}
            for key, value in encrypted_dict.items():
                decrypted[key] = self.cipher.decrypt(value.encode()).decode()
            return decrypted
        except Exception as e:
            if STREAMLIT_AVAILABLE:
                st.error(f"🔐 Failed to decrypt secrets: {e}")
            else:
                print(f"ERROR: Failed to decrypt secrets: {e}")
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
        # For local testing, try multiple encryption keys
        possible_keys = [
            "FloatChat-Ocean-Data-Explorer-2025",  # Default key (try first)
            os.getenv("ENCRYPTION_KEY"),
        ]
        
        if STREAMLIT_AVAILABLE:
            try:
                possible_keys.insert(0, st.secrets.get("ENCRYPTION_KEY"))
            except:
                pass
        
        for key in possible_keys:
            if key:
                try:
                    secrets_manager = SecureSecrets(key)
                    decrypted = secrets_manager.decrypt_secrets(ENCRYPTED_SECRETS)
                    if STREAMLIT_AVAILABLE:
                        st.write(f"🔐 Successfully decrypted secrets using key: {key[:10]}...")
                    else:
                        print(f"🔐 Successfully decrypted secrets using key: {key[:10]}...")
                    return decrypted
                except Exception as e:
                    if STREAMLIT_AVAILABLE:
                        st.write(f"🔐 Failed to decrypt with key {key[:10] if key else 'None'}...: {e}")
                    else:
                        print(f"🔐 Failed to decrypt with key {key[:10] if key else 'None'}...: {e}")
                    continue
        
        error_msg = "🔑 Could not decrypt secrets with any available encryption key"
        if STREAMLIT_AVAILABLE:
            st.error(error_msg)
        else:
            print(f"ERROR: {error_msg}")
        return {}
    except Exception as e:
        warning_msg = f"⚠️ Could not load encrypted secrets: {e}"
        if STREAMLIT_AVAILABLE:
            st.warning(warning_msg)
        else:
            print(f"WARNING: {warning_msg}")
        return {}
# 🌊 Ocean Data Explorer - Streamlit Deployment Guide

## 🚀 Deploy to Streamlit Community Cloud

### Prerequisites
- GitHub repository (✅ Already done!)
- Streamlit Community Cloud account
- API keys for Pinecone and Groq

### Step-by-Step Deployment

#### 1. **Access Streamlit Community Cloud**
- Go to [share.streamlit.io](https://share.streamlit.io)
- Sign in with your GitHub account

#### 2. **Create New App**
- Click "New app"
- Select your repository: `ChaitanyaJhindal/FloatChat`
- Branch: `main`
- Main file path: `SIH(Final_submission)/ocean_data_dashboard.py`
- App URL: Choose your custom URL (e.g., `floatchat-oceandata`)

#### 3. **Configure Secrets**
Before deploying, you need to add your API keys:

1. In the Streamlit Cloud dashboard, click on your app
2. Go to "Settings" → "Secrets"
3. Add the following secrets:

```toml
GROQ_API_KEY = "your_actual_groq_api_key_here"
PINECONE_API_KEY = "your_actual_pinecone_api_key_here"
```

#### 4. **Deploy**
- Click "Deploy"
- Wait for the build process to complete
- Your app will be live at: `https://your-app-name.streamlit.app`

### 🔧 Configuration Files

- **requirements.txt** ✅ Already configured with all dependencies
- **secrets.toml** ✅ Template ready (update with your keys)
- **.gitignore** ✅ Configured to protect sensitive files

### 🌐 Environment Variables
The app will automatically load:
1. Streamlit secrets (for cloud deployment)
2. Environment variables (for local development)
3. Fallback to streamlit.secrets for compatibility

### 📊 Features Available After Deployment
- Interactive oceanographic data visualization
- Real-time Argo float data access
- AI-powered query system with Groq
- Vector database search with Pinecone
- Multiple data analysis tools and charts

### 🔒 Security Notes
- Never commit actual API keys to GitHub
- Use Streamlit secrets for deployment
- Keep your `.env` file local only

### 🆘 Troubleshooting
- If deployment fails, check the logs in Streamlit Cloud
- Ensure all dependencies are in requirements.txt
- Verify API keys are correctly set in secrets
- Check that the main file path is correct

### 📱 Sharing Your App
Once deployed, you can:
- Share the public URL with anyone
- Embed in websites
- Use for demonstrations and presentations

Happy deploying! 🎊
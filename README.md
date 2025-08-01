AI Resume Analyzer is a Streamlit web app that uses the Google Gemini Pro Vision API to analyze resumes in PDF format. It extracts content, understands structure, and provides smart career feedback to help users improve their resumes.

✅ Prerequisites
Python 3.10+

A valid Google Gemini API key

Poppler installed and configured in PATH (for PDF rendering)

🔧 Setup Instructions
1. Clone the Repo

git clone https://github.com/gaurav-daware/Resume-Analyzer.git
cd Resume-Analyzer
2. Create and Activate a Virtual Environment
bash
python -m venv venv
venv\Scripts\activate       # On Windows
# OR
source venv/bin/activate    # On Mac/Linux
3. Install Dependencies

pip install -r requirements.txt
4. Install Poppler (Required for pdf2image)
Windows:
Download from https://github.com/oschwartz10612/poppler-windows/releases/
Extract the zip and add the bin/ folder to System Environment PATH

Mac/Linux:

brew install poppler         # Mac (Homebrew)
sudo apt install poppler-utils  # Ubuntu/Debian

5. Set Up .env File
Create a file named .env in the root directory:
GOOGLE_API_KEY=your_google_gemini_api_key
▶️ Run the App


streamlit run app.py
Open http://localhost:8501 in your browser.


🧪 Example Usage (optional)
Upload your PDF resume and get AI-generated insights for improvement directly in your browser!


from dotenv import load_dotenv
load_dotenv()
import base64
import streamlit as st
import os
import io
from PIL import Image
import pdf2image
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# --- Helper Functions ---
def get_gemini_response(input_prompt, pdf_content_parts, additional_text=""):
    model = genai.GenerativeModel('models/gemini-1.5-flash')
    # Combine all input for the model
    full_input = [input_prompt] + pdf_content_parts
    if additional_text:
        full_input.append(additional_text)
    response = model.generate_content(full_input)
    return response.text

def input_pdf_setup_all_pages(uploaded_file):
    if uploaded_file is not None:
        images = pdf2image.convert_from_bytes(uploaded_file.read())
        pdf_parts = []
        for img in images:
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()
            pdf_parts.append(
                {
                    "mime_type": "image/jpeg",
                    "data": base64.b64encode(img_byte_arr).decode()
                }
            )
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")

# --- Streamlit App ---
st.set_page_config(page_title="Advanced ATS Resume & Cover Letter Expert", layout="wide")

# Custom CSS for styling
st.write("✅ App is running!")
st.markdown("""
<style>
.stApp {
    background-color: #f0f2f6;
    color: #333333;
}
.stButton>button {
    background-color: #1A73E8; /* Google Blue */
    color: white;
    font-weight: bold;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    margin: 5px;
    cursor: pointer;
    transition: background-color 0.3s;
}
.stButton>button:hover {
    background-color: #0F62CC;
}
h1, h2, h3 {
    color: #1A73E8; /* Google Blue */
}
.stTextArea, .stFileUploader {
    background-color: white;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.stSuccess {
    background-color: #e6ffe6;
    color: #006400;
    border-radius: 5px;
    padding: 10px;
    margin-top: 10px;
}
.stSpinner > div > span {
    color: #1A73E8;
}
</style>
""", unsafe_allow_html=True)

st.title("💡 AI-Powered Resume & Cover Letter Optimizer")
st.markdown("Your intelligent assistant for crafting job-winning applications.")

# --- Layout for Inputs ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 Job Description")
    job_description_text = st.text_area(
        "Paste the full job description here:",
        key="job_desc_input",
        height=300,
        placeholder="e.g., 'We are looking for a Data Scientist with expertise in Python, machine learning, and cloud platforms...'"
    )

with col2:
    st.subheader("⬆️ Upload Your Resume")
    uploaded_resume_file = st.file_uploader("Upload your resume (PDF)...", type=["pdf"])

    if uploaded_resume_file is not None:
        st.success("Resume Uploaded Successfully!")
        # Store PDF content in session state for re-use
        try:
            st.session_state['pdf_content_parts'] = input_pdf_setup_all_pages(uploaded_resume_file)
            st.session_state['resume_uploaded'] = True
        except FileNotFoundError as e:
            st.error(str(e))
            st.session_state['resume_uploaded'] = False
    else:
        st.session_state['resume_uploaded'] = False
        st.info("Please upload your resume to get started.")

st.subheader("📄 Upload Your Cover Letter (Optional)")
uploaded_cover_letter_file = st.file_uploader("Upload your cover letter (PDF or Text)...", type=["pdf", "txt"])
cover_letter_text_area = st.text_area("Or paste your Cover Letter here:", key="cover_letter_text_input", height=200, placeholder="Paste your cover letter text here...")

# Process uploaded cover letter if it's a PDF (as text)
if uploaded_cover_letter_file:
    if uploaded_cover_letter_file.type == "application/pdf":
        try:
            # For PDF cover letters, you'd need a PDF to text library or use Gemini to extract text
            # This is a simplified example, a dedicated PDF text extraction is better
            images = pdf2image.convert_from_bytes(uploaded_cover_letter_file.read())
            cover_letter_extracted_text = ""
            for img in images:
                # Use OCR for text extraction if needed, otherwise rely on model's ability
                # For simplicity, we'll let Gemini extract text from image if it's treated as image input
                pass
            st.warning("PDF cover letter uploaded. The model will interpret it as an image for analysis. For best text extraction, paste text or upload a .txt file if possible.")
        except Exception as e:
            st.error(f"Error processing PDF cover letter: {e}")
            uploaded_cover_letter_file = None
    elif uploaded_cover_letter_file.type == "text/plain":
        cover_letter_text_area = uploaded_cover_letter_file.read().decode("utf-8")
        st.session_state['cover_letter_content'] = cover_letter_text_area
        st.success("Cover Letter (Text) Uploaded Successfully!")

# Use the text area content as primary cover letter input
cover_letter_input = cover_letter_text_area if cover_letter_text_area else st.session_state.get('cover_letter_content', "")


# --- Analysis Buttons & Prompts ---
st.markdown("---")
st.subheader("✨ Get Detailed Analysis")

# Define prompts (keep them concise for better model performance)
PROMPT_RESUME_EVAL = """
You are an experienced Technical Human Resource Manager. Review the provided resume against the job description.
Provide a professional evaluation highlighting the candidate's strengths and weaknesses in relation to the job requirements.
Focus on:
1.  **Overall Suitability:** Does the candidate seem like a good fit?
2.  **Key Strengths:** What stands out positively?
3.  **Areas for Improvement:** What could be enhanced or added?
"""

PROMPT_PERCENTAGE_MATCH = """
You are an ATS (Applicant Tracking System) scanner expert.
Evaluate the resume against the provided job description and give a percentage match.
Your response MUST follow this exact format:
PERCENTAGE_MATCH: [XX%]
MISSING_KEYWORDS: [List of critical keywords from JD missing in resume, comma-separated. If none, state 'None'.]
FINAL_THOUGHTS: [Concise summary of ATS compatibility and suggestions for improvement.]
"""

PROMPT_FORMATTING_READABILITY = """
You are a resume design and readability expert. Analyze the resume's formatting for ATS compatibility and human readability.
Provide feedback on:
-   **Layout & Visuals:** Is it clean, professional, and easy to scan? Are there elements that might confuse an ATS?
-   **Consistency:** Are fonts, headings, and bullet points consistent?
-   **White Space Usage:** Is there appropriate white space to prevent overcrowding?
-   **Actionable Advice:** How can the formatting be improved for better impact and ATS parsing?
"""

PROMPT_QUANTIFIABLE_ACHIEVEMENTS = """
You are a career coach specializing in resume optimization. Review the candidate's resume and the job description.
Identify specific bullet points or sections where achievements could be strengthened by adding quantifiable metrics (numbers, percentages, results).
For each identified point, provide a suggested rephrase that includes a measurable outcome.
Example: "Instead of 'Managed projects', consider 'Managed 5+ projects, reducing delivery time by 15%'."
"""

PROMPT_ACTION_VERBS = """
You are a linguistic expert for resume writing. Analyze the action verbs used throughout the resume (especially in experience and project sections).
Highlight instances where stronger, more dynamic action verbs could replace weaker or passive phrasing.
Provide alternative suggestions for improvement.
"""

PROMPT_SKILL_GAP_ANALYSIS = """
You are a career development specialist. Based on the job description and the resume, identify specific technical and soft skills that are mentioned in the job description but are either missing or weakly represented in the resume.
For each skill gap, suggest concrete ways to acquire or demonstrate proficiency, including:
-   **Online Courses/Certifications:** Specific platforms or course types (e.g., Coursera, Udemy, Google Certifications).
-   **Projects:** Types of personal or open-source projects.
-   **Resources:** Relevant books, tutorials, or communities.
"""

PROMPT_COVER_LETTER_ANALYSIS = """
You are a senior recruiter. Analyze the provided cover letter against the job description and, if a resume is also provided, consider its consistency with the resume.
Evaluate:
-   **Tailoring:** How well it addresses specific points in the job description.
-   **Impact & Persuasion:** Is it compelling and clearly convey the candidate's value?
-   **Clarity & Conciseness:** Is it easy to read and understand?
-   **Consistency with Resume:** Does it complement the resume without simply repeating it?
-   **Improvements:** Provide actionable advice to enhance its effectiveness.
"""


# Create expanders for organizing analysis options
with st.expander("🚀 Resume Analysis"):
    col_res1, col_res2, col_res3 = st.columns(3)
    with col_res1:
        submit1 = st.button("🌟 Overall Resume Evaluation")
    with col_res2:
        submit3 = st.button("📊 Percentage Match & Keywords")
    with col_res3:
        submit4 = st.button("🎨 Formatting & Readability")

    col_res4, col_res5, col_res6 = st.columns(3)
    with col_res4:
        submit5 = st.button("📈 Quantifiable Achievements")
    with col_res5:
        submit6 = st.button("💪 Action Verb Enhancement")
    with col_res6:
        submit_skills = st.button("💡 Skill Gap & Learning Path")


with st.expander("✉️ Cover Letter Analysis"):
    submit_cover_letter = st.button("Analyze Cover Letter")


# --- Response Display Logic ---
if st.session_state.get('resume_uploaded', False) or (cover_letter_input and uploaded_cover_letter_file): # Allow cover letter analysis even without resume
    if submit1:
        if st.session_state.get('resume_uploaded', False):
            with st.spinner("Analyzing resume..."):
                response = get_gemini_response(PROMPT_RESUME_EVAL, st.session_state['pdf_content_parts'], job_description_text)
                st.subheader("Resume Evaluation")
                st.write(response)
        else:
            st.warning("Please upload your resume for this analysis.")

    elif submit3:
        if st.session_state.get('resume_uploaded', False):
            with st.spinner("Calculating match percentage..."):
                response = get_gemini_response(PROMPT_PERCENTAGE_MATCH, st.session_state['pdf_content_parts'], job_description_text)
                st.subheader("Percentage Match & Keywords")
                st.write(response)
        else:
            st.warning("Please upload your resume for this analysis.")

    elif submit4:
        if st.session_state.get('resume_uploaded', False):
            with st.spinner("Analyzing formatting..."):
                response = get_gemini_response(PROMPT_FORMATTING_READABILITY, st.session_state['pdf_content_parts']) # JD not strictly needed here
                st.subheader("Formatting & Readability Analysis")
                st.write(response)
        else:
            st.warning("Please upload your resume for this analysis.")

    elif submit5:
        if st.session_state.get('resume_uploaded', False):
            with st.spinner("Suggesting quantifiable achievements..."):
                response = get_gemini_response(PROMPT_QUANTIFIABLE_ACHIEVEMENTS, st.session_state['pdf_content_parts'], job_description_text)
                st.subheader("Quantifiable Achievements Suggestions")
                st.write(response)
        else:
            st.warning("Please upload your resume for this analysis.")

    elif submit6:
        if st.session_state.get('resume_uploaded', False):
            with st.spinner("Improving action verbs..."):
                response = get_gemini_response(PROMPT_ACTION_VERBS, st.session_state['pdf_content_parts']) # JD not strictly needed
                st.subheader("Action Verb Enhancement")
                st.write(response)
        else:
            st.warning("Please upload your resume for this analysis.")

    elif submit_skills:
        if st.session_state.get('resume_uploaded', False):
            if job_description_text:
                with st.spinner("Identifying skill gaps..."):
                    response = get_gemini_response(PROMPT_SKILL_GAP_ANALYSIS, st.session_state['pdf_content_parts'], job_description_text)
                    st.subheader("Skill Gap Analysis & Learning Paths")
                    st.write(response)
            else:
                st.warning("Please provide the Job Description to identify skill gaps.")
        else:
            st.warning("Please upload your resume and provide the Job Description for this analysis.")

    elif submit_cover_letter:
        if cover_letter_input or uploaded_cover_letter_file: # Check if any cover letter content exists
            with st.spinner("Analyzing cover letter..."):
                # Combine resume content if available for more comprehensive analysis
                all_inputs = []
                if st.session_state.get('resume_uploaded', False):
                    all_inputs = st.session_state['pdf_content_parts'] # Pass resume as image if needed for context
                # Pass cover letter text directly for analysis
                combined_text_for_cl = f"Job Description: {job_description_text}\n\nCover Letter: {cover_letter_input}"
                response = get_gemini_response(PROMPT_COVER_LETTER_ANALYSIS, all_inputs, combined_text_for_cl)
                st.subheader("Cover Letter Analysis")
                st.write(response)
        else:
            st.warning("Please provide a Cover Letter (upload or paste) for analysis.")

else:
    st.info("Upload your resume and/or cover letter, and paste the job description to start the analysis!")

st.markdown("---")

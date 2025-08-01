from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv() # Load your GOOGLE_API_KEY from .env
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    print("Error: GOOGLE_API_KEY not found in .env file.")
    exit()

try:
    genai.configure(api_key=API_KEY)
    print("API configured.")

    # --- Step 1: List ALL available models and identify the correct names ---
    print("\n--- Listing ALL available Gemini models: ---")
    available_gemini_pro_name = None
    available_gemini_pro_vision_name = None

    for m in genai.list_models():
        print(f"  - Name: {m.name}, Display Name: {m.display_name}, Methods: {m.supported_generation_methods}")

        # Check for text-only model (like gemini-pro)
        if m.name == 'models/gemini-pro' and 'generateContent' in m.supported_generation_methods:
            available_gemini_pro_name = m.name
        elif m.display_name == 'Gemini 1.0 Pro' and 'generateContent' in m.supported_generation_methods:
            available_gemini_pro_name = m.name
        elif m.name == 'models/gemini-1.0-pro' and 'generateContent' in m.supported_generation_methods:
            available_gemini_pro_name = m.name # This is often the correct one

        # Check for multimodal model (like gemini-pro-vision)
        if m.name == 'models/gemini-pro-vision' and 'generateContent' in m.supported_generation_methods:
            available_gemini_pro_vision_name = m.name
        elif m.display_name == 'Gemini 1.0 Pro Vision' and 'generateContent' in m.supported_generation_methods:
            available_gemini_pro_vision_name = m.name
        elif m.name == 'models/gemini-1.0-pro-vision' and 'generateContent' in m.supported_generation_methods:
            available_gemini_pro_vision_name = m.name # This is often the correct one
        elif m.name == 'models/gemini-1.5-flash' and 'generateContent' in m.supported_generation_methods:
            available_gemini_pro_vision_name = m.name # 1.5-flash is also multimodal

    if available_gemini_pro_name:
        print(f"\nIdentified correct Gemini Pro model name: {available_gemini_pro_name}")
    else:
        print("\nCould not find a suitable 'gemini-pro' equivalent that supports generateContent.")

    if available_gemini_pro_vision_name:
        print(f"Identified correct Gemini Pro Vision model name: {available_gemini_pro_vision_name}")
    else:
        print("Could not find a suitable 'gemini-pro-vision' equivalent that supports generateContent.")


    # --- Step 2: Attempt a simple text generation using the identified name ---
    if available_gemini_pro_name:
        print(f"\nAttempting a simple text generation using: {available_gemini_pro_name}")
        model = genai.GenerativeModel(available_gemini_pro_name)
        response = model.generate_content("Hello, Gemini!")
        print("\n--- Text Model API Call Successful! ---")
        print(f"Response: {response.text}")
    else:
        print("\nSkipping text model test as no suitable model was found.")

except Exception as e:
    print("\n--- An Unexpected Error Occurred ---")
    print(f"Error: {e}")
    print("\nThis might indicate a deeper API key permission issue or network problem preventing even model listing.")
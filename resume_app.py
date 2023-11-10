import streamlit as st
from langchain.llms import GooglePalm
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import fitz  # PyMuPDF

# Initialize GooglePalm LLM
api = "AIzaSyCE8GPxkKGibdVtSpL4SooR_7hS7auBzWI"
llm = GooglePalm(google_api_key=api, temperature=0)

# Function to extract text from PDF using PyMuPDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ''

    for page_num in range(doc.page_count):
        page = doc[page_num]
        text += page.get_text()

    doc.close()
    return text

# Function to generate analysis result
def generate_result(pdf_path):
    st.info("Analyzing the resume... Please wait.")
    prompt_template_resume = PromptTemplate(
        input_variables=['text'],
        template="Analyze the {text} resume and provide the job suited for it and also give ATS check and dont give all the details, just give the analysis. Also, don't give any salary expectations.  Also give strengths and weakness of the resume and suggest some changes.Give everything in detail",
    )
    model = LLMChain(llm=llm, prompt=prompt_template_resume)
    resume_text = extract_text_from_pdf(pdf_path=pdf_path)
    result = model.run({'text': resume_text})
    return result

# Streamlit app with custom CSS
def main():
    # Custom CSS for styling
    st.markdown(
        """
        <style>
            body {
                background-color: #f8f9fa;
            }
            
            .stButton {
                background-color: #007bff;
                color: white;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("📄 Resume Analysis App")
    st.markdown("Upload a PDF file to get a personalized analysis of the resume.")

    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

    if uploaded_file is not None:
        # Save the uploaded file to a known location
        with open("uploaded_resume.pdf", "wb") as f:
            f.write(uploaded_file.getvalue())

        st.info("Analyzing the resume... Please wait.")
        result = generate_result("uploaded_resume.pdf")  # Pass the saved path

        st.markdown("### 🚀 Analysis Result:")
        st.write(result)

        st.success("Analysis complete! Feel free to upload another resume.")

if __name__ == '__main__':
    main()

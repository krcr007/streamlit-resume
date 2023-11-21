import streamlit as st

from pdfminer.high_level import extract_text

from langchain.llms import GooglePalm
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os

# Initialize LangChain
api = "AIzaSyCE8GPxkKGibdVtSpL4SooR_7hS7auBzWI"
llm = GooglePalm(google_api_key=api, temperature=0)

# PDF text extraction
def extract_text_from_pdf(pdf_path):
  return extract_text(pdf_path)

# Generate analysis
def generate_result(pdf_path):

    st.info("Analyzing the resume... Please wait.")
    prompt_template_resume = PromptTemplate(
        input_variables=['text'],
        template="Analyze the {text} resume and provide the job suited for it and also give ATS check and dont give all the details, just give the analysis. Also, don't give any salary expectations.  Also give strengths and weakness of the resume and suggest some changes.Give everthing in detail",)
    model = LLMChain(llm=llm, prompt=prompt_template_resume)
    resume_text = extract_text_from_pdf(pdf_path=pdf_path)
    result = model.run({'text': resume_text})
    return result


def analyze_resumes_in_folder(folder_path, job_role):
    resumes = []
    scores = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            resume_path = os.path.join(folder_path, filename)
            resume_text = extract_text_from_pdf(pdf_path=resume_path)

            # Generate analysis for each resume
            result = model.run({'text': resume_text})

            # Save resume and corresponding score
            resumes.append({'Resume': filename, 'ATS Score': result['ATS Score'], 'Job Role': result['Predicted Job Role']})

    # Create a DataFrame for easy sorting
    df = pd.DataFrame(resumes)

    # Filter resumes by specified job role
    df = df[df['Job Role'].str.contains(job_role, case=False)]

    # Sort resumes by ATS Score
    df = df.sort_values(by='ATS Score', ascending=False).head(10)

    return df

import io

# ... (previous code)

def employer_section():
    st.header("👔 Employer Section")

    uploaded_folder = st.file_uploader("Upload resumes", type=["zip", "pdf"], key="upload_folder", accept_multiple_files=True)

    if uploaded_folder:
        job_role = st.text_input("Enter the job role you are looking for:")

        if st.button("Analyze Resumes"):
            top_resumes_df = analyze_resumes_in_folder(uploaded_folder, job_role)

            st.info("Analyzing resumes... Please wait.")
            st.markdown(f"### 🎯 Top 10 Resumes for the specified job role ({job_role}):")
            st.table(top_resumes_df[['Resume', 'ATS Score']])


def student_section():
    st.header("📄 Resume Analysis App")

    uploaded_file = st.file_uploader("Choose a PDF", type=["pdf"])

    if uploaded_file:
        # Use st.file_uploader as a context manager
        with uploaded_file as f:
            with open("resume.pdf", "wb") as resume_file:
                resume_file.write(f.read())

        result = generate_result("resume.pdf")

        st.markdown("### 🚀 Analysis Result:")
        st.write(result)

        st.success("Analysis complete!")

def main():
    st.sidebar.title("Switch Between Sections")
    section = st.sidebar.radio("Select Section:", ["Student", "Employer"])

    if section == "Student":
        student_section()
    elif section == "Employer":
        employer_section()

if __name__ == '__main__':
    main()





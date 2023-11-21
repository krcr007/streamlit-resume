import streamlit as st
from pdfminer.high_level import extract_text
from langchain.llms import GooglePalm
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os
import io
import zipfile
import pandas as pd

# Initialize LangChain
api = "AIzaSyCE8GPxkKGibdVtSpL4SooR_7hS7auBzWI"
llm = GooglePalm(google_api_key=api, temperature=0)

# PDF text extraction
def extract_text_from_pdf(pdf_path):
    return extract_text(pdf_path)

# Generate analysis
def generate_result(resume_text):
    st.info("Analyzing the resume... Please wait.")
    prompt_template_resume = PromptTemplate(
        input_variables=['text'],
        template="Analyze the {text} resume and provide the job suited for it and also give ATS check and don't give all the details, just give the analysis. Also, don't give any salary expectations. Also, give strengths and weaknesses of the resume and suggest some changes. Give everything in detail",
    )
    model = LLMChain(llm=llm, prompt=prompt_template_resume)
    result = model.run({'text': resume_text})

    # Extract relevant information from the result
    analysis_result = {
        'ATS Score': result.get('ATS Score', 0),  # Provide a default value if 'ATS Score' is not present
        'Predicted Job Role': result.get('Predicted Job Role', 'Unknown'),  # Provide a default value if 'Predicted Job Role' is not present
    }

    return analysis_result


def analyze_resumes_in_folder(uploaded_folder, job_role):
    resumes = []

    # Check if the uploaded content is a zip file
    is_zip = any(file.name.endswith('.zip') for file in uploaded_folder)

    if is_zip:
        with io.BytesIO() as zip_buffer:
            # Write the content of all files into the buffer
            for file in uploaded_folder:
                zip_buffer.write(file.read())

            with zipfile.ZipFile(zip_buffer, 'r') as zip_ref:
                # Extract the contents of the zip file to a temporary directory
                temp_dir = 'temp_folder'
                zip_ref.extractall(temp_dir)

                # Iterate through the extracted files
                for filename in os.listdir(temp_dir):
                    file_path = os.path.join(temp_dir, filename)
                    if filename.endswith('.pdf') and os.path.isfile(file_path):
                        resume_text = extract_text_from_pdf(file_path)

                        # Generate analysis for each resume
                        result = generate_result(resume_text)

                        # Save resume and corresponding score
                        resumes.append({'Resume': filename, 'ATS Score': result['ATS Score'], 'Job Role': result['Predicted Job Role']})

        # Remove the temporary directory
        os.rmdir(temp_dir)

    else:
        # If the files are not in a zip archive, assume they are individual PDF files
        for uploaded_file in uploaded_folder:
            resume_text = extract_text_from_pdf(io.BytesIO(uploaded_file.read()))

            # Generate analysis for each resume
            result = generate_result(resume_text)

            # Save resume and corresponding score
            resumes.append({'Resume': uploaded_file.name, 'ATS Score': result['ATS Score'], 'Job Role': result['Predicted Job Role']})

    # Create a DataFrame for easy sorting
    df = pd.DataFrame(resumes)

    # Filter resumes by specified job role
    df = df[df['Job Role'].str.contains(job_role, case=False)]

    # Sort resumes by ATS Score
    df = df.sort_values(by='ATS Score', ascending=False).head(10)

    return df

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
            resume_text = extract_text_from_pdf(io.BytesIO(f.read()))

        result = generate_result(resume_text)

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

import streamlit as st

from pdfminer.high_level import extract_text

from langchain.llms import GooglePalm
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

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
        template="Analyze the {text} resume and provide the job suited for it and also give ATS check and dont give all the details, just give the analysis.Dont give any salary expectations details in it.  Also give strengths and weakness of the resume and suggest some changes.Give everthing in detail",)
    model = LLMChain(llm=llm, prompt=prompt_template_resume)
    resume_text = extract_text_from_pdf(pdf_path=pdf_path)
    result = model.run({'text': resume_text})
    return result

def main():

  st.markdown("""
    <style>
    body {
      background-color: #f8f9fa;
    }
    .stButton {
      background-color: #007bff;
      color: white;   
    }
    </style>
    """, unsafe_allow_html=True)

  st.title("📄 Resume Analysis App")

  uploaded_file = st.file_uploader("Choose a PDF", type=["pdf"])

  if uploaded_file:
    with open("resume.pdf","wb") as f:
      f.write(uploaded_file.getvalue())

    result = generate_result("resume.pdf")

    st.markdown("### 🚀 Analysis Result:")
    st.write(result)

    st.success("Analysis complete!")

if __name__ == '__main__':
  main()

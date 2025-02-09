import os
import streamlit as st
import openai
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
import datetime

# Load OpenAI API key from .env file
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OpenAI API key is missing! Please set it in the .env file.")

client = openai.OpenAI(api_key=api_key)

# Function to extract key details from pasted email
def extract_project_details(email_text):
    prompt = f"""
    Analyze the following email and extract structured information for a design brief. 
    Identify key elements: Client Name, Project Type, Deliverables, Timeline, Services, and any other relevant information. 

    Email Content:
    ----------------------
    {email_text}
    ----------------------

    Format the extracted information in this structure:
    - **Client Name:** [Client Name]
    - **Project Type:** [Project Type]
    - **Deliverables:** [List of Deliverables]
    - **Timeline:** [Dates for different stages]
    - **Services:** [Services to be provided]
    - **Other Notes:** [Any other key details]
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are an expert project manager extracting details from client emails."},
                  {"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

# Function to save the generated design brief as a PDF
def save_as_pdf(text, filename="design_brief.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    
    title_style = styles["Title"]
    title_style.textColor = colors.HexColor("#004aad")  # Deep blue title

    heading_style = styles["Heading2"]
    heading_style.textColor = colors.HexColor("#0077b6")  # Light blue headings

    body_style = styles["BodyText"]
    body_style.fontSize = 12

    elements = []

    elements.append(Paragraph("🎨 Design Brief", title_style))
    elements.append(Spacer(1, 0.2 * inch))

    sections = text.split("**")
    
    for i in range(1, len(sections), 2):
        heading = sections[i].strip()
        content = sections[i + 1].strip() if i + 1 < len(sections) else ""

        elements.append(Paragraph(heading, heading_style))
        elements.append(Spacer(1, 0.1 * inch))
        elements.append(Paragraph(content, body_style))
        elements.append(Spacer(1, 0.2 * inch))

    doc.build(elements)

# Streamlit UI
st.set_page_config(page_title="Design Brief Generator", page_icon="📄", layout="wide")

st.title("📩 AI-Powered Design Brief Generator")
st.write("Paste a client email, and the AI will extract key details and generate a structured design brief.")

email_text = st.text_area("📥 Paste Client Email Here", height=250)

if st.button("🚀 Generate Design Brief"):
    if email_text.strip():
        with st.spinner("Extracting details from the email... ⏳"):
            extracted_details = extract_project_details(email_text)
        
        with st.spinner("Generating structured design brief... ⏳"):
            design_brief = extract_project_details(email_text)

        st.subheader("📄 Generated Design Brief")
        st.text_area("", design_brief, height=300)

        pdf_filename = f"Design_Brief_{datetime.date.today()}.pdf"
        save_as_pdf(design_brief, pdf_filename)

        with open(pdf_filename, "rb") as file:
            st.download_button("📥 Download PDF", file, file_name=pdf_filename)

    else:
        st.warning("⚠️️ ️ Please paste an email before generating the brief.")

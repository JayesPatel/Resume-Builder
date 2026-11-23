# Resume Builder

# Name
# email
# Phone
# Education
# Experience
# Skills


import streamlit as st
import requests
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
import re
from reportlab.pdfbase.pdfmetrics import stringWidth

st.title("Resume Bulder")

name = st.text_input("Enter Your Name")
email = st.text_input("Enter Your Email")
phone = st.text_input("Enter Your Mobile No")
linkedin = st.text_input("Enter Your LinkedIn Profile")
github = st.text_input("Enter Your GitHub Profile")

education = st.text_area("Enter Your Education")
project = st.text_area("Enter Your Project")
skills = st.text_area("Enter Your Skills")
exp = st.text_area("Enter Your Experience")

if st.button("Generate Resume"):
    if not name or not email or not phone or not exp or not project or not skills :
        st.warning("Please Fill All details")
    else:
        with st.spinner("Generation Resume...."):
            key = st.secrets["OPENROUTER_API_KEY"]  # Replace with your actual OpenRouter API key
            url = "https://openrouter.ai/api/v1/chat/completions"

            headers = {
                "Authorization":f"Bearer {key}",
                "Content-Type":"application/json"
            }
            body={
                "model":"openai/gpt-4o-mini",
                "messages":[
                    {
                        "role":"user",
                        "content": f"""
Create a professional fresher resume using these details:

Name: {name}
Email: {email}
Phone: {phone}
Education: {education}
Skills: {skills}
Projects: {project}
Experience: {exp}

IMPORTANT FORMATTING RULES:

1. Start directly with Objective.
2. Do not write introductions like "Sure! Below is..."
3. Do not repeat the candidate's name, email or phone.
4. Do not include LinkedIn or GitHub in Additional Information.
5. Do not generate placeholders such as [Your University Name].
6. Do not invent any information.
7. Use these headings:
   Objective
   Education
   Skills
   Projects
   Experience
   Certifications (only if provided)
8. Use clear bullet points.
9. Keep the resume professional and ATS-friendly.
10. Do not add unnecessary notes or explanations.
"""
                    }
                ]
            }

            try:
                response = requests.post(
                    url,
                    headers=headers,
                    json=body,
                    timeout=60
                    )
                response.raise_for_status()
                # Server Statur
                data = response.json()
                result = data["choices"][0]["message"]["content"]
                st.success("Resume Generated Sucessfully")
                st.markdown(result)

                
                # Generate PDF

                pdfBuffer = BytesIO()

                pdf = canvas.Canvas(
                pdfBuffer,
                pagesize=A4
                )

                width, height = A4
                left_margin = 50
                right_margin = 50
                y = height - 50

                # Name
                pdf.setFont("Helvetica-Bold", 16)
                pdf.drawString(50, y, name)

                y -= 25

                # Email and Phone
                pdf.setFont("Helvetica", 10)
                pdf.drawString(50, y, f"Email: {email} | Phone: {phone}")

                y -= 20

                # LinkedIn
                if linkedin:
                    pdf.drawString(50, y, f"LinkedIn: {linkedin}")
                    y -= 20

                # GitHub
                if github:
                    pdf.drawString(50, y, f"GitHub: {github}")
                    y -= 20

                y -= 20
                # Clean Markdown symbols
                def clean_text(line):
                    line = line.strip()

                    # Remove horizontal separators
                    if re.match(r"^[-*_]{3,}$", line):
                        return ""

                        # Remove heading symbols
                    line = re.sub(r"^#{1,6}\s*", "", line)

                    # Remove bold and italic symbols
                    line = line.replace("**", "")
                    line = line.replace("__", "")
                    line = line.replace("*", "")
                    line = line.replace("_", "")

                    return line.strip()


                # Draw Resume Content
                for line in result.split("\n"):

                    line = clean_text(line)

                    if not line:
                        y -= 8
                        continue

                    # Bullet points
                    if line.startswith("- "):
                        line = "• " + line[2:]

                    pdf.setFont("Helvetica", 10)

                    # Automatic text wrapping
                    words = line.split()
                    current_line = ""

                    for word in words:

                        test_line = current_line + " " + word if current_line else word

                        if stringWidth(test_line, "Helvetica", 10) < width - left_margin - right_margin:
                            current_line = test_line

                        else:
                            if y < 50:
                                pdf.showPage()
                                y = height - 50

                            pdf.drawString(left_margin, y, current_line)
                            y -= 16
                            current_line = word

                    if current_line:
                        if y < 50:
                            pdf.showPage()
                            y = height - 50

                        pdf.drawString(left_margin, y, current_line)
                        y -= 16

                pdf.save()
                pdfBuffer.seek(0)

                st.download_button(
                    label="Download CV in PDF",
                    data=pdfBuffer,
                    file_name="My_CV.pdf",
                    mime="application/pdf"
                )

            except Exception as e:
                st.error(e)       

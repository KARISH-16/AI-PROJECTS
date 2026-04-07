import sqlite3
import streamlit as st
import pandas as pd
import base64, random
import time, datetime
from pdfminer3.layout import LAParams
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer3.converter import TextConverter
import io
from streamlit_tags import st_tags
from PIL import Image
from Courses import ds_course, web_course, android_course, ios_course, uiux_course, resume_videos, interview_videos
import plotly.express as px

# ---------------- PDF READER ----------------
def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)

    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh):
            page_interpreter.process_page(page)

    text = fake_file_handle.getvalue()
    converter.close()
    fake_file_handle.close()
    return text

# ---------------- SHOW PDF ----------------
def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# ---------------- COURSE RECOMMENDER ----------------
def course_recommender(course_list):
    st.subheader("🎓 Course Recommendations")
    rec_course = []
    no_of_reco = st.slider('Choose Number of Courses:', 1, 10, 4)
    random.shuffle(course_list)

    for i, (c_name, c_link) in enumerate(course_list):
        st.markdown(f"{i+1}. [{c_name}]({c_link})")
        rec_course.append(c_name)
        if i+1 == no_of_reco:
            break
    return rec_course

# ---------------- DATABASE ----------------
connection = sqlite3.connect('resume_parser.db')
cursor = connection.cursor()

# ---------------- STREAMLIT CONFIG ----------------
st.set_page_config(page_title="Smart Resume Analyzer", page_icon='./Logo/SRA_Logo.png')

# ---------------- MAIN FUNCTION ----------------
def run():
    st.title("📄 Smart Resume Analyzer")

    st.sidebar.title("Choose User")
    choice = st.sidebar.selectbox("Select", ["Normal User", "Admin"])

    # Load logo
    try:
        img = Image.open('./Logo/logo.png')
        st.image(img.resize((200,200)))
    except:
        st.warning("Logo not found")

    # ---------------- NORMAL USER ----------------
    if choice == 'Normal User':
        pdf_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

        if pdf_file:
            save_path = './Uploaded_Resumes/' + pdf_file.name

            with open(save_path, "wb") as f:
                f.write(pdf_file.getbuffer())

            show_pdf(save_path)

            # Extract text
            resume_text = pdf_reader(save_path)

            # ---------------- SIMPLE SKILL EXTRACTION ----------------
            name = "User"
            skills = []

            keywords = [
                "Python", "Java", "C++", "Machine Learning", "AI",
                "Data Science", "SQL", "HTML", "CSS", "JavaScript"
            ]

            for word in keywords:
                if word.lower() in resume_text.lower():
                    skills.append(word)

            # ---------------- DISPLAY ----------------
            st.header("📊 Resume Analysis")
            st.success(f"Hello {name}")

            st.subheader("Detected Skills")
            st.write(skills)

            # ---------------- SCORE ----------------
            st.subheader("Resume Score")
            score = 0

            if 'objective' in resume_text.lower(): score += 20
            if 'declaration' in resume_text.lower(): score += 20
            if 'hobbies' in resume_text.lower(): score += 20
            if 'achievements' in resume_text.lower(): score += 20
            if 'projects' in resume_text.lower(): score += 20

            st.progress(score)
            st.success(f"Score: {score}%")

            # ---------------- COURSES ----------------
            if "Python" in skills or "Data Science" in skills:
                course_recommender(ds_course)
            elif "HTML" in skills or "CSS" in skills:
                course_recommender(web_course)

            # ---------------- VIDEOS ----------------
            st.header("🎥 Resume Tips")
            st.video(random.choice(resume_videos))

            st.header("🎥 Interview Tips")
            st.video(random.choice(interview_videos))

    # ---------------- ADMIN ----------------
    else:
        st.header("Admin Login")
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")

        if st.button("Login"):
            if user == "admin" and pwd == "admin":
                st.success("Welcome Admin")

                data = pd.read_sql("SELECT * FROM user_data", connection)
                st.dataframe(data)
            else:
                st.error("Invalid Credentials")

# ---------------- RUN ----------------
run()

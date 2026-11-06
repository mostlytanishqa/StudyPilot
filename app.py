
import streamlit as st
import pandas as pd
import plotly.express as px

from datetime import date

import database as db
from config import TAGLINE
from learning_hub import render_learning_hub
from study_planner import generate_schedule




# ==========================================
# WELCOME PAGE
# ==========================================

def render_welcome():

    st.markdown("""
    <div style="
        background: linear-gradient(120deg,#172554,#4F46E5);
        padding: 45px 25px;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin-bottom: 30px;
    ">
        <h1 style="font-size: 45px; color:white;">
            🎓 STUDYPILOT
        </h1>

        <h2 style="color:white;">
            Welcome to Smart Learning
        </h2>

        <p style="color:#DCE6FF;font-size:17px;">
            Learn Smarter. Practise Better. Improve Faster.
        </p>

        <span style="
            background:#14B8A6;
            padding:8px 20px;
            border-radius:20px;
            font-weight:bold;
        ">
            TE-B PROJECT
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        "<h2 style='text-align:center;color:#172554;'>"
        "Meet Our Project Team</h2>",
        unsafe_allow_html=True
    )

    team = [
        ("Parth Unde", "52"),
        ("Ajinkya Walse", "55"),
        ("Taniska Zende", "59"),
        ("Snehal Thorat", "51")
    ]

    columns = st.columns(2)

    for index, (name, roll) in enumerate(team):

        with columns[index % 2]:

            with st.container(border=True):

                st.markdown(
                    "<h2 style='text-align:center;'>👤</h2>",
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"<h3 style='text-align:center;color:#4F46E5;'>"
                    f"{name}</h3>",
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"<p style='text-align:center;'>"
                    f"Roll Number: {roll}</p>",
                    unsafe_allow_html=True
                )

    st.divider()

    st.markdown(
        "<h3 style='text-align:center;color:#4F46E5;'>"
        "TE-B PROJECT CO-ORDINATOR</h3>",
        unsafe_allow_html=True
    )

    st.markdown("""
    <div style="
        background:#EEF2FF;
        padding:22px;
        border-radius:14px;
        text-align:center;
    ">
        <h3 style="color:#172554;">
            StudyPilot
        </h3>
        <p style="color:#475569;">
            Smart Learning, Revision & Exam Preparation Platform
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    if st.button(
        "🚀 Enter StudyPilot Dashboard",
        type="primary",
        use_container_width=True
    ):
        st.session_state["welcome_entered"] = True
        st.rerun()


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="StudyPilot | Smart Learning",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

db.initialize_database()


# ==========================================
# CUSTOM DESIGN
# ==========================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background-color: #F5F7FC;
}

[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #111B32,
        #1B2945
    );
}

[data-testid="stSidebar"] * {
    color: #F1F5F9;
}

.hero {
    background: linear-gradient(
        120deg,
        #172554,
        #4F46E5
    );
    padding: 30px;
    border-radius: 18px;
    color: white;
    margin-bottom: 25px;
}

.hero h1 {
    color: white;
    font-size: 34px;
    font-weight: 800;
}

.hero p {
    color: #DCE6FF;
}

.metric-card {
    background: white;
    border: 1px solid #E5EAF3;
    padding: 22px;
    border-radius: 15px;
    min-height: 125px;
    box-shadow: 0 3px 12px rgba(15,23,42,0.04);
}

.metric-title {
    color: #64748B;
    font-size: 13px;
}

.metric-value {
    color: #172554;
    font-size: 29px;
    font-weight: 800;
    margin-top: 8px;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# SIDEBAR NAVIGATION
# ==========================================

with st.sidebar:

    st.markdown("# 🎓 StudyPilot")

    st.caption(
        "Your Personal Learning Companion"
    )

    st.divider()

    page = st.radio(
        "MAIN MENU",
        [
            "Dashboard",
            "Study Planner",
            "Learning Hub",
            "Settings / About"
        ]
    )

    st.divider()

    student = db.get_student()

    st.markdown("### 👤 Student Profile")

    st.write(student["name"])

    st.caption(
        f"Daily availability: {student['daily_hours']} hours"
    )

    st.divider()

    st.caption(TAGLINE)


# ==========================================
# DASHBOARD
# ==========================================

def render_dashboard():

    student = db.get_student()

    stats = db.get_dashboard_stats()

    st.markdown(f"""
    <div class="hero">
        <h1>Welcome back, {student['name']}! 👋</h1>
        <p>{TAGLINE}</p>
        <p>Your academic preparation journey starts here.</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Your Learning Overview")

    c1, c2, c3, c4 = st.columns(4)

    cards = [
        ("Total Subjects", stats["subjects"]),
        ("Completed Topics", stats["completed"]),
        ("Pending Topics", stats["pending"]),
        ("Preparation", f"{stats['percentage']}%")
    ]

    for col, (label, value) in zip(
        [c1, c2, c3, c4],
        cards
    ):

        with col:

            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">{label}</div>
                <div class="metric-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)

    st.write("")

    left, right = st.columns(2)

    # Progress chart
    with left:

        st.subheader("Preparation Progress")

        if stats["total_topics"] > 0:

            fig = px.pie(
                names=["Completed", "Pending"],
                values=[
                    stats["completed"],
                    stats["pending"]
                ],
                hole=0.72,
                color_discrete_sequence=[
                    "#14B8A6",
                    "#E2E8F0"
                ]
            )

            fig.update_layout(
                height=300,
                margin=dict(t=15, b=15)
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            st.progress(
                stats["percentage"] / 100,
                text=f"{stats['percentage']}% completed"
            )

        else:
            st.info("Add topics to view your progress.")

    # Weekly study chart
    with right:

        st.subheader("Weekly Study Activity")

        activity = db.get_weekly_activity()

        if activity:

            df = pd.DataFrame(activity)

            fig = px.bar(
                df,
                x="study_date",
                y="hours",
                color_discrete_sequence=["#6366F1"],
                labels={
                    "study_date": "Date",
                    "hours": "Study Hours"
                }
            )

            fig.update_layout(
                height=300,
                showlegend=False
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info(
                "Your study activity will appear "
                "after your first study session."
            )

    # Upcoming exams
    st.subheader("📅 Upcoming Examinations")

    exams = db.get_upcoming_exams()

    if exams:

        exam_df = pd.DataFrame(exams)

        exam_df["Days Remaining"] = exam_df[
            "exam_date"
        ].apply(
            lambda x: (
                date.fromisoformat(x) - date.today()
            ).days
        )

        exam_df.columns = [
            "Subject",
            "Exam Date",
            "Days Remaining"
        ]

        st.dataframe(
            exam_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No upcoming examinations.")

    # Study logging
    st.subheader("📝 Log Your Study Activity")

    subjects = db.get_subjects()

    if subjects:

        subject_map = {
            s["name"]: s["id"]
            for s in subjects
        }

        with st.form("study_log_form"):

            selected = st.selectbox(
                "Select Subject",
                list(subject_map.keys())
            )

            hours = st.number_input(
                "Study Duration (Hours)",
                min_value=0.25,
                max_value=16.0,
                value=1.0,
                step=0.25
            )

            submitted = st.form_submit_button(
                "Save Study Session",
                use_container_width=True
            )

            if submitted:

                db.save_study_session(
                    subject_map[selected],
                    hours
                )

                st.success("Study session saved!")

                st.rerun()

    # Recommended activity
    st.subheader("🎯 Recommended Next Activity")

    pending = [
        topic for topic in db.get_topics()
        if not topic["completed"]
    ]

    if pending:

        next_topic = pending[0]

        st.info(
            f"Continue studying **{next_topic['name']}** "
            f"under **{next_topic['subject_name']}**. "
            f"Difficulty: {next_topic['difficulty']}."
        )

    else:

        st.success(
            "Congratulations! All topics are completed."
        )


# ==========================================
# STUDY PLANNER
# ==========================================

def render_planner():

    st.title("📅 Smart Study Planner")

    st.write(
        "Organize your subjects and create "
        "a personalized study timetable."
    )

    subjects = db.get_subjects()

    left, right = st.columns(2)

    # Add subject
    with left:

        st.subheader("➕ Add New Subject")

        with st.form("subject_form"):

            subject_name = st.text_input(
                "Subject Name",
                placeholder="Example: Mathematics"
            )

            exam_date = st.date_input(
                "Examination Date",
                min_value=date.today()
            )

            submitted = st.form_submit_button(
                "Add Subject",
                use_container_width=True
            )

            if submitted:

                if not subject_name.strip():

                    st.error("Enter a subject name.")

                else:

                    try:

                        db.add_subject(
                            subject_name,
                            exam_date.isoformat()
                        )

                        st.success("Subject added!")

                        st.rerun()

                    except Exception:

                        st.error(
                            "Subject already exists or "
                            "could not be added."
                        )

    # Add topic
    with right:

        st.subheader("➕ Add New Topic")

        if subjects:

            subject_map = {
                s["name"]: s["id"]
                for s in subjects
            }

            with st.form("topic_form"):

                selected_subject = st.selectbox(
                    "Select Subject",
                    list(subject_map.keys())
                )

                topic_name = st.text_input(
                    "Topic Name",
                    placeholder="Example: Algebra"
                )

                difficulty = st.selectbox(
                    "Difficulty",
                    ["Easy", "Medium", "Hard"]
                )

                submitted = st.form_submit_button(
                    "Add Topic",
                    use_container_width=True
                )

                if submitted:

                    if not topic_name.strip():

                        st.error("Enter a topic name.")

                    else:

                        db.add_topic(
                            subject_map[selected_subject],
                            topic_name,
                            difficulty
                        )

                        st.success("Topic added!")

                        st.rerun()

        else:

            st.info("Add a subject first.")

    st.divider()

    # Display topics
    st.subheader("📚 Your Topics")

    topics = db.get_topics()

    if topics:

        for topic in topics:

            with st.container(border=True):

                col1, col2, col3 = st.columns(
                    [3, 1, 1]
                )

                with col1:

                    st.write(
                        f"**{topic['name']}**"
                    )

                    st.caption(
                        topic["subject_name"]
                    )

                with col2:

                    st.write(
                        topic["difficulty"]
                    )

                with col3:

                    st.checkbox(
                        "Completed",
                        value=bool(topic["completed"]),
                        key=f"topic_{topic['id']}",
                        on_change=lambda tid=topic["id"]:
                            db.update_topic_status(
                                tid,
                                st.session_state[
                                    f"topic_{tid}"
                                ]
                            )
                    )

    else:

        st.info("No topics available.")

    st.divider()

    # Generate timetable
    st.subheader("🧠 Generate Smart Timetable")

    student = db.get_student()

    daily_hours = st.number_input(
        "Available study hours per day",
        min_value=0.5,
        max_value=16.0,
        value=float(student["daily_hours"]),
        step=0.5
    )

    if st.button(
        "Generate My Study Schedule",
        type="primary",
        use_container_width=True
    ):

        try:

            schedule = generate_schedule(
                db.get_topics(),
                daily_hours
            )

            db.save_schedule(schedule)

            db.update_student(
                student["name"],
                daily_hours
            )

            st.session_state["schedule_generated"] = True

            st.success("Your timetable is ready!")

        except ValueError as error:

            st.error(str(error))

    # Display timetable
    if st.session_state.get("schedule_generated"):

        schedule = db.get_schedule()

        st.subheader("📋 Your Generated Timetable")

        if schedule:

            schedule_df = pd.DataFrame(schedule)

            display_df = schedule_df.rename(
                columns={
                    "study_date": "Date",
                    "subject_name": "Subject",
                    "topic_name": "Topic",
                    "hours": "Study Hours"
                }
            )

            st.dataframe(
                display_df[
                    ["Date", "Subject", "Topic", "Study Hours"]
                ],
                use_container_width=True,
                hide_index=True
            )

            fig = px.bar(
                schedule_df,
                x="study_date",
                y="hours",
                color="subject_name",
                title="Daily Study Schedule",
                labels={
                    "study_date": "Date",
                    "hours": "Study Hours",
                    "subject_name": "Subject"
                }
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info("No pending topics to schedule.")


# ==========================================
# SETTINGS AND ABOUT
# ==========================================

def render_settings():

    st.title("⚙️ Settings / About")

    student = db.get_student()

    st.subheader("Student Profile")

    with st.form("profile_form"):

        name = st.text_input(
            "Student Name",
            value=student["name"]
        )

        hours = st.number_input(
            "Daily Study Availability",
            min_value=0.5,
            max_value=16.0,
            value=float(student["daily_hours"]),
            step=0.5
        )

        submitted = st.form_submit_button(
            "Save Profile",
            use_container_width=True
        )

        if submitted:

            if not name.strip():

                st.error("Name cannot be empty.")

            else:

                db.update_student(
                    name,
                    hours
                )

                st.success("Profile updated!")

                st.rerun()

    st.divider()

    st.subheader("About StudyPilot")

    st.markdown("""
    ### StudyPilot

    **Learn Smarter. Practise Better. Improve Faster.**

    StudyPilot is an educational platform designed
    to help college students prepare for examinations.

    **Problem Statement**

    Students often struggle to organize their preparation,
    identify weak topics and monitor their academic progress.

    **Proposed Solution**

    StudyPilot provides an integrated learning environment
    with personalized planning, educational resources
    and academic progress tracking.

    **Technology Stack**

    - Python 3.11+
    - Streamlit
    - SQLite
    - Pandas
    - NumPy
    - Plotly

    **Project Type:** Undergraduate Engineering Mini-Project.
    """)


# ==========================================
# MAIN PAGE ROUTING
# ==========================================

if page == "Dashboard":

    render_dashboard()

elif page == "Study Planner":

    render_planner()

elif page == "Learning Hub":

    render_learning_hub()

elif page == "Settings / About":

    render_settings()

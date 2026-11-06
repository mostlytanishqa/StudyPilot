
import json
import streamlit as st

from config import SUBJECTS_PATH


def load_learning_content():
    """Load educational content from JSON."""

    try:
        with open(
            SUBJECTS_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except FileNotFoundError:
        st.error("Learning content file not found.")
        return {}

    except json.JSONDecodeError:
        st.error("Invalid JSON format in subjects.json.")
        return {}


def render_learning_hub():

    st.title("📚 Learning Hub")

    st.caption(
        "Understand concepts. Build knowledge. "
        "Learn at your own pace."
    )

    content = load_learning_content()

    if not content:
        return

    # Subject selection
    subject = st.selectbox(
        "Choose your subject",
        list(content.keys())
    )

    subject_data = content[subject]

    st.info(subject_data["description"])

    # Topic selection
    topic = st.selectbox(
        "Select a topic",
        list(subject_data["topics"].keys())
    )

    topic_data = subject_data["topics"][topic]

    st.divider()

    st.subheader(f"📖 {topic}")

    # Introduction
    with st.expander(
        "Introduction",
        expanded=True
    ):
        st.write(topic_data["introduction"])

    # Important concepts
    with st.expander(
        "💡 Important Concepts",
        expanded=True
    ):

        for concept in topic_data["concepts"]:
            st.markdown(f"- {concept}")

    # Formula
    with st.expander("🧮 Formula"):

        st.code(
            topic_data["formula"],
            language=None
        )

    # Solved example
    with st.expander(
        "✏️ Solved Example",
        expanded=True
    ):
        st.write(topic_data["example"])

    # Important points
    with st.expander("⭐ Important Points"):

        for point in topic_data["important"]:
            st.markdown(f"- {point}")

    st.divider()

    st.success(
        "Lesson completed? Continue practising "
        "to strengthen your understanding!"
    )

import streamlit as st
import sys
import os
import tempfile

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from acronym_finder import load_document, find_acronyms, find_screenshots, find_tables
from llm_helper import generate_glossary_definition, generate_image_description
from database import create_table, save_entry, get_all_entries
from main import add_glossary_to_document
from docx import Document

st.set_page_config(
    page_title="Doc Automation Tool",
    page_icon="📄",
    layout="centered"
)

create_table()

# ── Header ────────────────────────────────────────────────────
st.title("📄 Document Automation Tool")
st.markdown("Automatically detect acronyms, generate definitions using AI, and add descriptions to screenshots and tables.")
st.divider()

# ── Step 1: File Upload ───────────────────────────────────────
st.subheader("Step 1 — Upload your document")
uploaded_file = st.file_uploader("Choose a .docx file", type=["docx"])

if uploaded_file is not None:

    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    paragraphs = load_document(tmp_path)
    acronyms = find_acronyms(paragraphs)
    screenshots = find_screenshots(tmp_path)
    tables = find_tables(tmp_path)

    st.success(f"Document loaded! Found {len(paragraphs)} paragraph(s), {len(screenshots)} screenshot(s), {len(tables)} table(s).")

    with st.expander("View document content"):
        for i, para in enumerate(paragraphs, 1):
            st.write(f"{i}. {para}")

    st.divider()

    # ── Step 2: Confirm Acronyms ──────────────────────────────
    st.subheader("Step 2 — Confirm acronyms")

    if not acronyms:
        st.warning("No acronyms detected.")
        confirmed = []
    else:
        st.write(f"Found **{len(acronyms)}** potential acronym(s). Uncheck any that are NOT real acronyms:")
        confirmed = []
        for acronym in acronyms:
            if st.checkbox(acronym, value=True, key=f"check_{acronym}"):
                confirmed.append(acronym)

    st.divider()

    # ── Step 3: Expansions and Definitions ───────────────────
    if confirmed:
        st.subheader("Step 3 — Expansions and definitions")
        st.write("For each acronym, enter the expansion. Then choose how to handle the definition.")

        acronym_data = {}

        for acronym in confirmed:
            st.markdown(f"#### {acronym}")

            expansion = st.text_input(
                f"Full form of {acronym}:",
                key=f"exp_{acronym}",
                placeholder="e.g. Application Programming Interface"
            )

            if expansion:
                # Ask user: write definition yourself or let AI do it?
                def_choice = st.radio(
                    f"Definition for {acronym}:",
                    options=["I will write it myself", "Let AI generate it"],
                    key=f"choice_{acronym}",
                    horizontal=True
                )

                if def_choice == "I will write it myself":
                    user_def = st.text_area(
                        "Write your definition:",
                        key=f"userdef_{acronym}",
                        placeholder="Type your definition here..."
                    )
                    acronym_data[acronym] = {
                        "expansion": expansion,
                        "definition": user_def,
                        "mode": "manual"
                    }
                else:
                    acronym_data[acronym] = {
                        "expansion": expansion,
                        "definition": None,
                        "mode": "ai"
                    }

            st.write("")

        st.divider()

        # ── Step 4: Screenshot and Table Descriptions ─────────
        media_data = []

        if screenshots or tables:
            st.subheader("Step 4 — Screenshot and table descriptions")

            if screenshots:
                st.write("**Screenshots detected:**")
                for i, shot in enumerate(screenshots):
                    st.markdown(f"**Screenshot {i+1}:** `{shot['placeholder']}`")
                    st.caption(f"Context: {shot['context']}")

                    desc_choice = st.radio(
                        "How to handle this description?",
                        options=["I will write it myself", "Let AI generate it"],
                        key=f"shotchoice_{i}",
                        horizontal=True
                    )

                    if desc_choice == "I will write it myself":
                        user_desc = st.text_input(
                            "Write description:",
                            key=f"shotdesc_{i}",
                            placeholder="e.g. Figure shows the login page of the system"
                        )
                        media_data.append({
                            "type": "screenshot",
                            "index": shot["index"],
                            "context": shot["context"],
                            "description": user_desc,
                            "mode": "manual"
                        })
                    else:
                        media_data.append({
                            "type": "screenshot",
                            "index": shot["index"],
                            "context": shot["context"],
                            "description": None,
                            "mode": "ai"
                        })

            if tables:
                st.write("**Tables detected:**")
                for i, tbl in enumerate(tables):
                    st.markdown(f"**Table {i+1}:** `{tbl['preview']}`")
                    st.caption(f"Context: {tbl['context']}")

                    desc_choice = st.radio(
                        "How to handle this description?",
                        options=["I will write it myself", "Let AI generate it"],
                        key=f"tblchoice_{i}",
                        horizontal=True
                    )

                    if desc_choice == "I will write it myself":
                        user_desc = st.text_input(
                            "Write description:",
                            key=f"tbldesc_{i}",
                            placeholder="e.g. Table shows the API response codes"
                        )
                        media_data.append({
                            "type": "table",
                            "index": tbl["index"],
                            "context": tbl["context"],
                            "description": user_desc,
                            "mode": "manual"
                        })
                    else:
                        media_data.append({
                            "type": "table",
                            "index": tbl["index"],
                            "context": tbl["context"],
                            "description": None,
                            "mode": "ai"
                        })

            st.divider()

        # ── Step 5: Generate and Review ───────────────────────
        st.subheader("Step 5 — Generate and review")

        if st.button("Process document", type="primary"):
            glossary_entries = []
            final_media = []

            # Handle acronym definitions
            st.write("**Processing acronyms...**")
            for acronym, data in acronym_data.items():
                if data["mode"] == "ai":
                    with st.spinner(f"AI generating definition for {acronym}..."):
                        definition = generate_glossary_definition(acronym, data["expansion"])
                else:
                    definition = data["definition"]

                save_entry(acronym, data["expansion"], definition)
                glossary_entries.append((acronym, data["expansion"], definition))
                st.write(f"✅ {acronym}({data['expansion']})")
                st.caption(f"↳ {definition}")

            # Handle media descriptions
            if media_data:
                st.write("**Processing screenshots and tables...**")
                for item in media_data:
                    if item["mode"] == "ai":
                        with st.spinner(f"AI generating description for {item['type']}..."):
                            description = generate_image_description(item["context"])
                    else:
                        description = item["description"]

                    final_media.append({**item, "description": description})
                    st.write(f"✅ {item['type'].capitalize()} description ready")
                    st.caption(f"↳ {description}")

            st.session_state["glossary_entries"] = glossary_entries
            st.session_state["final_media"] = final_media
            st.session_state["tmp_path"] = tmp_path
            st.success("All done! Review below and download your updated document.")

        # ── Step 6: Download ──────────────────────────────────
        if "glossary_entries" in st.session_state:
            st.divider()
            st.subheader("Step 6 — Download updated document")

            output_path = add_glossary_to_document(
                st.session_state["tmp_path"],
                st.session_state["glossary_entries"]
            )

            with open(output_path, "rb") as f:
                st.download_button(
                    label="Download document with glossary",
                    data=f,
                    file_name="document_with_glossary.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    type="primary"
                )

# ── Sidebar ───────────────────────────────────────────────────
st.sidebar.title("Saved glossary entries")
entries = get_all_entries()
if entries:
    for entry in entries:
        _, acronym, expansion, definition, created_at = entry
        st.sidebar.markdown(f"**{acronym}** ({expansion})")
        st.sidebar.caption(created_at)
else:
    st.sidebar.info("No entries saved yet.")
import streamlit as st
import os
from src.generate_outline import load_outline_from_file, extract_outline_metadata, parse_outline
from src.generate_parts import run_generate_parts_for_all
from src.generate_contents import run_generate_contents_and_save_book

st.set_page_config(page_title="📘 Book Generator", layout="centered")
st.title("📘 AI Textbook Generator")

uploaded_file = st.file_uploader("Upload your outline.md", type=["md"])

if uploaded_file:
    os.makedirs("src", exist_ok=True)
    with open("src/outline.md", "wb") as f:
        f.write(uploaded_file.read())

    raw_outline = load_outline_from_file("src/outline.md")
    metadata = extract_outline_metadata(raw_outline)

    st.subheader("📄 Book Metadata")
    st.markdown(f"**Title:** {metadata['title']}")
    st.markdown(f"**Audience:** {metadata['audience']}")
    st.markdown(f"**Description:** {metadata['description']}")
    st.markdown("**Objectives:**")
    for obj in metadata["objectives"]:
        st.markdown(f"- {obj}")
    # Parse and display table of contents
    chapters, sections, items = parse_outline(raw_outline)

    st.subheader("📚 Outline Preview")

    for chap_idx, chapter in enumerate(chapters):
        st.markdown(f"### Chapter {chap_idx + 1}: {chapter}")

        for sec_idx, section in enumerate(sections[chap_idx]):
            st.markdown(f"- **Section {chap_idx + 1}.{sec_idx + 1}**: {section}")

            for item_idx, item in enumerate(items[chap_idx][sec_idx]):
                st.markdown(f"    - {item}")

    st.divider()

    debug = st.checkbox("Enable Debug Mode (Chapter 1 only)", value=True)
    output_dir = st.text_input("Output Directory", value="book_output")

    if st.button("🚀 Generate Book"):
        with st.spinner("Generating textbook..."):
            try:
                run_generate_contents_and_save_book(output_dir=output_dir, debug=debug)
                st.success(f"✅ Book generated in `{output_dir}`")

                book_path = os.path.join(output_dir, f"{metadata['title']}.txt")
                if os.path.exists(book_path):
                    with open(book_path, "r", encoding="utf-8") as book_file:
                        st.download_button("📥 Download Book", book_file.read(), file_name=os.path.basename(book_path))
            except Exception as e:
                st.error(f"❌ Generation failed: {e}")

import streamlit as st
import os
from src.generate_outline import load_outline_from_file, extract_outline_metadata, parse_outline
from src.generate_parts import run_generate_parts_for_all
from src.generate_contents import run_generate_contents_and_save_book

# ─────────────────────────────────────────────────────────────────────────────
# Session State Initialization
# ─────────────────────────────────────────────────────────────────────────────
if "preview_ready" not in st.session_state:
    st.session_state.preview_ready = False

if "preview_approved" not in st.session_state:
    st.session_state.preview_approved = False

if "run_full_after_preview" not in st.session_state:
    st.session_state.run_full_after_preview = False

# ─────────────────────────────────────────────────────────────────────────────
# Page Setup
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="📘 Book Generator", layout="centered")
st.title("📘 AI Textbook Generator")

# ─────────────────────────────────────────────────────────────────────────────
# Supporting Document Upload (Optional)
# ─────────────────────────────────────────────────────────────────────────────
supporting_text = ""
supporting_files = st.file_uploader(
    "Upload optional supporting document(s)", type=["txt", "md", "pdf"], accept_multiple_files=True
)

if supporting_files:
    st.markdown("✅ Support files uploaded:")
    for f in supporting_files:
        st.markdown(f"- {f.name}")
        if f.type in ["text/plain", "text/markdown"]:
            supporting_text += f.read().decode("utf-8") + "\n\n"
        elif f.type == "application/pdf":
            try:
                import PyPDF2
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        supporting_text += text + "\n"
            except Exception as e:
                st.warning(f"⚠️ Could not extract from {f.name}: {e}")

# ─────────────────────────────────────────────────────────────────────────────
# Outline Upload
# ─────────────────────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader("Upload your outline.md", type=["md"])

if uploaded_file:
    os.makedirs("src", exist_ok=True)
    with open("src/outline.md", "wb") as f:
        f.write(uploaded_file.read())

    raw_outline = load_outline_from_file("src/outline.md")
    metadata = extract_outline_metadata(raw_outline)

    # ─────────────────────────────────────────────────────────────────────────
    # Display Metadata and TOC
    # ─────────────────────────────────────────────────────────────────────────
    st.subheader("📄 Book Metadata")
    st.markdown(f"**Title:** {metadata['title']}")
    st.markdown(f"**Audience:** {metadata['audience']}")
    st.markdown(f"**Description:** {metadata['description']}")
    st.markdown("**Objectives:**")
    for obj in metadata["objectives"]:
        st.markdown(f"- {obj}")

    chapters, sections, items = parse_outline(raw_outline)

    st.subheader("📚 Outline Preview")
    for chap_idx, chapter in enumerate(chapters):
        st.markdown(f"### Chapter {chap_idx + 1}: {chapter}")
        for sec_idx, section in enumerate(sections[chap_idx]):
            st.markdown(f"- **Section {chap_idx + 1}.{sec_idx + 1}**: {section}")
            for item_idx, item in enumerate(items[chap_idx][sec_idx]):
                st.markdown(f"    - {item}")

    st.divider()

    # ─────────────────────────────────────────────────────────────────────────
    # Controls
    # ─────────────────────────────────────────────────────────────────────────
    preview_mode = st.checkbox("🔍 Preview Mode (generate only first part)", value=True)
    output_dir = st.text_input("Output Directory", value="book_output")

    # ─────────────────────────────────────────────────────────────────────────
    # Preview Workflow
    # ─────────────────────────────────────────────────────────────────────────
    if preview_mode and not st.session_state.preview_approved:
        if st.button("👀 Generate Preview"):
            try:
                run_generate_contents_and_save_book(
                    output_dir=output_dir,
                    debug=True,
                    status_area=st.empty(),
                    live_output_area=st.container(),
                    extra_context=supporting_text
                )
                st.success("✅ Preview generated.")
                st.session_state.preview_ready = True
            except Exception as e:
                st.error(f"❌ Preview failed: {e}")

        if st.session_state.preview_ready:
            if st.button("✅ Approve & Continue Full Book Generation"):
                st.session_state.preview_approved = True
                st.session_state.run_full_after_preview = True
                st.experimental_rerun()

    # ─────────────────────────────────────────────────────────────────────────
    # Full Generation After Preview Approval
    # ─────────────────────────────────────────────────────────────────────────
    if st.session_state.run_full_after_preview:
        st.session_state.run_full_after_preview = False  # reset flag
        try:
            run_generate_contents_and_save_book(
                output_dir=output_dir,
                debug=False,
                status_area=st.empty(),     # show part progress
                live_output_area=None,      # don't stream content
                extra_context=supporting_text
            )
            st.success("✅ Full book generated after preview.")

            book_path_docx = os.path.join(output_dir, f"{metadata['title']}.docx")
            if os.path.exists(book_path_docx):
                with open(book_path_docx, "rb") as docx_file:
                    st.download_button("📥 Download DOCX", docx_file.read(), file_name=os.path.basename(book_path_docx))
        except Exception as e:
            st.error(f"❌ Full generation failed: {e}")

    # ─────────────────────────────────────────────────────────────────────────
    # Direct Full Generation (No Preview Mode)
    # ─────────────────────────────────────────────────────────────────────────
    if not preview_mode:
        if st.button("🚀 Generate Full Book"):
            try:
                run_generate_contents_and_save_book(
                    output_dir=output_dir,
                    debug=False,
                    status_area=st.empty(),     # show part names
                    live_output_area=None,      # don't stream full content
                    extra_context=supporting_text
                )
                st.success("✅ Full book generated.")

                book_path_docx = os.path.join(output_dir, f"{metadata['title']}.docx")
                if os.path.exists(book_path_docx):
                    with open(book_path_docx, "rb") as docx_file:
                        st.download_button("📥 Download DOCX", docx_file.read(), file_name=os.path.basename(book_path_docx))
            except Exception as e:
                st.error(f"❌ Full generation failed: {e}")

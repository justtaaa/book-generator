import os
from dotenv import load_dotenv
from openai import OpenAI
import re
from yaspin import yaspin

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
openai_endpoint = os.getenv("OPENAI_API_ENDPOINT")

if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_endpoint
)

def load_outline_from_file(filepath="outline.md"):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def extract_outline_metadata(outline_md: str) -> dict:
    """
    Extracts title, description, audience, and learning objectives from the outline markdown.
    Returns a dictionary with keys: title, description, audience, objectives.
    """
    metadata = {}

    title_match = re.search(r"## Title:\s*(.*)", outline_md)
    audience_match = re.search(r"## Audience:\s*(.*?)\n##", outline_md, re.DOTALL)
    description_match = re.search(r"## Description:\s*(.*?)\n##", outline_md, re.DOTALL)
    objectives_match = re.search(r"## Learning Objectives:\s*(.*?)(?:\n##|\Z)", outline_md, re.DOTALL)

    metadata["title"] = title_match.group(1).strip() if title_match else "Untitled Book"
    metadata["audience"] = audience_match.group(1).strip().replace("\n", " ") if audience_match else "Unspecified"
    metadata["description"] = description_match.group(1).strip().replace("\n", " ") if description_match else "No description provided."

    if objectives_match:
        objectives_raw = objectives_match.group(1).strip()
        metadata["objectives"] = [line.lstrip("- ").strip() for line in objectives_raw.splitlines() if line.strip().startswith("-")]
    else:
        metadata["objectives"] = []

    return metadata

def parse_outline(raw_outline: str):
    import re

    chapters = []
    sections = []
    items = []

    current_chapter_idx = -1
    current_section_idx = -1

    for line in raw_outline.splitlines():
        line = line.strip()
        if not line:
            continue

        chap_match = re.match(r"^### Chapter\s+(\d+)\.\s+(.*)", line)
        if chap_match:
            chapters.append(chap_match.group(2).strip())
            sections.append([])
            items.append([])
            current_chapter_idx += 1
            current_section_idx = -1
            continue

        sec_match = re.match(r"^#### Section\s+(\d+\.\d+)\s+(.*)", line)
        if sec_match:
            if current_chapter_idx == -1:
                raise ValueError("Section found before a chapter.")
            sections[current_chapter_idx].append(sec_match.group(2).strip())
            items[current_chapter_idx].append([])
            current_section_idx += 1
            continue

        item_match = re.match(r"^#####\s+(\d+\.\d+\.\d+)\s+(.*)", line)
        if item_match:
            if current_chapter_idx == -1 or current_section_idx == -1:
                raise ValueError("Item found before a chapter or section.")
            items[current_chapter_idx][current_section_idx].append(item_match.group(2).strip())
            continue

    return chapters, sections, items


if __name__ == "__main__":
    response = load_outline_from_file("outline.md")
    parse_outline(response)
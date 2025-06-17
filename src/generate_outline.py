import os
from dotenv import load_dotenv
from openai import OpenAI
import re
from yaspin import yaspin

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")

client = OpenAI(
    api_key=openai_api_key,
)

def load_outline_from_file(filepath="outline.md"):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def extract_title_and_description(outline_md: str) -> tuple[str, str]:
    import re

    title_match = re.search(r"## Title\s+\*\*(.*?)\*\*", outline_md, re.DOTALL)
    desc_match = re.search(r"## Description\s+(.*?)\n##", outline_md, re.DOTALL)

    title = title_match.group(1).strip() if title_match else "Untitled Book"
    description = desc_match.group(1).strip().replace('\n', ' ') if desc_match else "No description provided."

    return title, description


import re

def parse_outline(raw_outline: str):
    chapters = []
    sections = []
    items = []

    current_chapter_idx = -1
    current_section_idx = -1

    for line in raw_outline.splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        chapter_match = re.match(r"^### Chapter\s+\d+\.\s+(.*)$", stripped)
        if chapter_match:
            chapter_title = chapter_match.group(1).strip()
            chapters.append(chapter_title)
            sections.append([])
            items.append([])
            current_chapter_idx += 1
            current_section_idx = -1
            continue

        section_match = re.match(r"^#### Section\s+(\d+\.\d+)\s+(.*)$", stripped)
        if section_match:
            if current_chapter_idx == -1:
                raise ValueError("Section defined before any chapter.")
            section_title = section_match.group(2).strip()
            sections[current_chapter_idx].append(section_title)
            items[current_chapter_idx].append([])
            current_section_idx += 1
            continue

        item_match = re.match(r"^-\s*(\d+\.\d+\.\d+)\s+(.*)$", stripped)
        if item_match:
            if current_chapter_idx == -1 or current_section_idx == -1:
                raise ValueError("Item defined before any chapter or section.")
            item_text = item_match.group(2).strip()
            items[current_chapter_idx][current_section_idx].append(item_text)
            continue

    return chapters, sections, items


if __name__ == "__main__":
    response = load_outline_from_file("outline.md")
    parse_outline(response)
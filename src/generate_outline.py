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

def generate_outline(title: str, description: str):
    prompt = f"""
    Generate the Outline for the chapters, sections, and items of the sections of the book {title}.\n
    The description of the book is: {description}\n
    The result should be formatted as follows:\n
    # Outline\n
    Chapter 1. First chapter's name\n
    \tSection 1. Title of section 1 of chapter 1\n
    \t\t-Some item of the section\n
    \t\t-Another item\n
    \t\t-Some other matter addressed\n
    \t\t-A point about something\n
    \t\t-Some last point of the section\n
    \nTry to generate at least 5 sections per chapter, and 6 points per section, if possible.\n
    """
    
    response = client.chat.completions.create(
        model="gpt-4.1-2025-04-14",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content

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

        chap_match = re.match(r"^Chapter\s+\d+\.\s+(.*)$", stripped)
        if chap_match:
            chapter_title = chap_match.group(1).strip()
            chapters.append(chapter_title)

            # Start a new "row" in sections and items
            sections.append([])
            items.append([])
            current_chapter_idx += 1
            current_section_idx = -1
            continue

        sec_match = re.match(r"^Section\s+\d+\.\s+(.*)$", stripped)
        if sec_match:
            section_title = sec_match.group(1).strip()
            sections[current_chapter_idx].append(section_title)
            items[current_chapter_idx].append([])
            current_section_idx += 1
            continue
        
        item_match = re.match(r"^-\s*(.*)$", stripped)
        if item_match:
            item_text = item_match.group(1).strip()
            items[current_chapter_idx][current_section_idx].append(item_text)
            continue

    return chapters, sections, items


if __name__ == "__main__":
    response = generate_outline("The Art of Programming", "A comprehensive guide to mastering programming concepts, techniques, and best practices for aspiring and experienced developers.")
    parse_outline(response)
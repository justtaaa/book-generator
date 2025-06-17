import os
from dotenv import load_dotenv
from openai import OpenAI
from generate_outline import load_outline_from_file, parse_outline, extract_title_and_description
from tqdm import tqdm
import re

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")

client = OpenAI(
    api_key=openai_api_key,
)

def generate_parts(title: str, description: str, selectedChapter: int, chapters: list[str], selectedSection: int, sections: list[list[str]], selectedItem: int, items: list[list[list[str]]]) -> str:
    prompt = f"""
    You are a **textbook learning designer and author**, working on a book titled *"{title}"*.

    ### Book Description
    {description}

    ### Current Focus
    We are developing the structure for a subsection of the book:

    - **Chapter {selectedChapter + 1}:** {chapters[selectedChapter]}
    - **Section {selectedSection + 1}:** {sections[selectedChapter][selectedSection]}
    - **Subsection {selectedItem + 1}:** {items[selectedChapter][selectedSection][selectedItem]}

    ---

    ### Task
    Break down this subsection into a **clear, logical sequence of 4–6 parts**. These parts will become major subtopics or conceptual chunks that will later be developed into 1000-word textbook sections.

    Each part should:
    - Represent a distinct **concept, method, principle, or perspective**.
    - Be phrased as a **concise, self-contained title** (not a full sentence).
    - Progress in a **logical educational order** (intro → build-up → variations or use cases → advanced aspect → reflection or summary).

    These parts will serve as learning blocks for **second-year undergraduates** and **junior-level software developers**. Structure them to **scaffold knowledge gradually** and avoid overlap.

    ---

    ### Output Format
    Return the list in plain text, with each part as a bullet point (using a hyphen “-”).

    Example:
    - Introduction to the Topic
    - Key Concepts and Terminology
    - Practical Applications
    - Advanced Considerations
    - Summary and Reflection

    ---

    Now generate the list of parts for:
    **“{items[selectedChapter][selectedSection][selectedItem]}”**
    """

    
    response = client.chat.completions.create(
        model="gpt-4.1-2025-04-14",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    
    return response.choices[0].message.content

def parse_parts(raw_parts_text: str) -> list[str]:
    result = []
    for line in raw_parts_text.splitlines():
        match = re.match(r"^-\s*(.*)$", line.strip())
        if match:
            result.append(match.group(1).strip())
    return result


def run_generate_parts_for_all(title: str, description: str, chapters: list[str], sections: list[list[str]], items: list[list[list[str]]]):

    parts = {}
    
    total_parts = 0
    for chap_idx in range(len(chapters)):
        for sec_idx in range(len(sections[chap_idx])):
            total_parts += len(items[chap_idx][sec_idx])
    
    with tqdm(total=total_parts, desc="Generating book parts", unit="part") as pbar:
        for chap_idx, _ in enumerate(chapters):
            parts[chap_idx] = {}
            for sec_idx, _ in enumerate(sections[chap_idx]):
                parts[chap_idx][sec_idx] = {}
                for item_idx, _ in enumerate(items[chap_idx][sec_idx]):
                    generated_text = generate_parts(
                        title=title,
                        description=description,
                        selectedChapter=chap_idx,
                        chapters=chapters,
                        selectedSection=sec_idx,
                        sections=sections,
                        selectedItem=item_idx,
                        items=items
                    )
                    parsed_list = parse_parts(generated_text)
                    parts[chap_idx][sec_idx][item_idx] = parsed_list
                    
                    pbar.update(1)

    return parts

if __name__ == "__main__":
    raw_outline = load_outline_from_file("outline.md")
    book_title, book_description = extract_title_and_description(raw_outline)
    print("=== RAW OUTLINE ===")
    print(raw_outline)

    chapters, sections, items = parse_outline(raw_outline)

    all_generated = run_generate_parts_for_all(
        title=book_title,
        description=book_description,
        chapters=chapters,
        sections=sections,
        items=items
    )

    print("\n=== SAMPLE generate_parts OUTPUT ===")
    sample = all_generated[0][0][0]
    print(f"Chapter 1, Section 1, Item 1 →\n{sample}")
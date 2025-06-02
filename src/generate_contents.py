import os
from dotenv import load_dotenv
from openai import OpenAI
from generate_outline import generate_outline, parse_outline
from generate_parts import run_generate_parts_for_all
from tqdm import tqdm
from yaspin import yaspin
import textwrap

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")

client = OpenAI(
    api_key=openai_api_key,
)

def generate_contents(title: str, description: str, selectedChapter: int, selectedSection: int, selectedItem: int, selectedPart: int, part_title: str, previous_parts_titles: list[str], previous_parts_contents: list[str], chapters: list[str], sections: list[list[str]], items: list[list[list[str]]],) -> str:
    # 1) Build a short “context” block listing what prior parts covered
    context_block = ""
    if previous_parts_titles:
        context_block += "### Previously written parts for this item:\n"
        for idx, (ptitle, pcontent) in enumerate(zip(previous_parts_titles, previous_parts_contents)):
            context_block += f"{idx+1}. {ptitle} (summary):\n"
            # Include first ~50 words of each earlier part as a summary
            snippet = " ".join(pcontent.strip().split()[:50])
            context_block += f"\"{snippet}...\"\n\n"
        context_block += "\n"

    # 2) Instruct the model not to overlap
    prompt = f"""
    You are writing “The Art of Programming,” a comprehensive guide to mastering programming concepts, techniques, and best practices.

    Book title: {title}
    Book description: {description}

    We are currently in:
    Chapter {selectedChapter + 1}. {chapters[selectedChapter]}
    Section {selectedSection + 1}. {sections[selectedChapter][selectedSection]}
    Item {selectedItem + 1}. {items[selectedChapter][selectedSection][selectedItem]}

    Now write the content for:
    Part {selectedPart + 1}. {part_title}

    {textwrap.dedent(context_block)}

    **Instructions for this part:**
    - Produce **at least 1000 words**.
    - Focus **only** on “{part_title}.” 
    - Avoid repeating any ideas, examples, or phrasing that have already appeared in prior parts (see summaries above).
    - If you need to reference earlier parts for continuity, do so briefly and then build new material.
    - Keep tone and style consistent with previous parts.

    Begin now:
    """

    response = client.chat.completions.create(
        model="gpt-4.1-2025-04-14",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content


def run_generate_contents_and_save_book(book_title: str, book_description: str, output_dir: str = "book_output"):

    with yaspin(text="Generating the Outline...", color="yellow") as spinner:
        try:
            raw_outline = generate_outline(book_title, book_description)
            spinner.ok("✔")
        except Exception as e:
            spinner.fail("✘")
            print(f"Error generating outline: {e}")
            return
        
    chapters, sections, items = parse_outline(raw_outline)

    parts = run_generate_parts_for_all(
        title=book_title,
        description=book_description,
        chapters=chapters,
        sections=sections,
        items=items
    )
    
    total_parts = 0
    for c in range(len(chapters)):
        for s in range(len(sections[c])):
            for i in range(len(items[c][s])):
                total_parts += len(parts[c][s][i])

    # 1) Prepare output directory and file handle
    os.makedirs(output_dir, exist_ok=True)
    book_path = os.path.join(output_dir, f"{book_title}.txt")

    with open(book_path, "w", encoding="utf-8") as f:
        # ──────────────────────────────────────────────────────────────────────
        # A) Title Page
        # ──────────────────────────────────────────────────────────────────────
        f.write("=" * 80 + "\n")
        f.write(f"{book_title.center(80)}\n")
        if book_description:
            import textwrap
            wrapped_desc = textwrap.fill(book_description, width=80)
            f.write(wrapped_desc.center(80) + "\n")
        f.write("=" * 80 + "\n\n\n")

        # ──────────────────────────────────────────────────────────────────────
        # B) Table of Contents
        # ──────────────────────────────────────────────────────────────────────
        f.write("TABLE OF CONTENTS\n\n")

        for chap_idx, chap_title in enumerate(chapters):
            chap_number = chap_idx + 1
            f.write(f"Chapter {chap_number}. {chap_title}\n")

            for sec_idx, sec_title in enumerate(sections[chap_idx]):
                sec_number = sec_idx + 1
                f.write(f"    Section {sec_number}. {sec_title}\n")

                for item_idx, item_title in enumerate(items[chap_idx][sec_idx]):
                    item_number = item_idx + 1
                    f.write(f"        Item {item_number}. {item_title}\n")

                f.write("\n")  # blank line after each section
            f.write("\n")  # blank line after each chapter

        # ──────────────────────────────────────────────────────────────────────
        # C) Main Content
        # ──────────────────────────────────────────────────────────────────────
        f.write("=" * 80 + "\n\n")

        pbar = tqdm(total=total_parts, desc="Generating book contents", unit="part")
        # Now generate-and-write each part’s content in the proper order
        for c, chap_title in enumerate(chapters):
            f.write(f"CHAPTER {c+1}. {chap_title}\n\n")
            for s, sec_title in enumerate(sections[c]):
                f.write(f"SECTION {s+1}. {sec_title}\n\n")
                for i, item_title in enumerate(items[c][s]):
                    f.write(f"ITEM {i+1}. {item_title}\n\n")

                    previous_titles = []
                    previous_contents = []

                    for p, part_title in enumerate(parts[c][s][i]):
                        f.write(f"PART {p+1}. {part_title}\n\n")
                        
                        content_text = generate_contents(
                            title=book_title,
                            description=book_description,
                            selectedChapter=c,
                            selectedSection=s,
                            selectedItem=i,
                            selectedPart=p,
                            part_title=part_title,
                            previous_parts_titles=previous_titles,
                            previous_parts_contents=previous_contents,
                            chapters=chapters,
                            sections=sections,
                            items=items
                        )  

                        f.write(content_text.strip() + "\n\n")

                        previous_titles.append(part_title)
                        previous_contents.append(content_text)
                        
                        pbar.update(1)

                    f.write("\n")  # blank line after all parts in this item

                f.write("\n")  # blank line after all items in this section

            f.write("\n\n")  # blank line after each chapter
        
        pbar.close()
        
    print(f"📚 All contents generated and saved into:\n    {book_path}")
    
if __name__ == "__main__":
    book_title = "The Art of Programming"
    book_description = (
        "A comprehensive guide to mastering programming concepts, "
        "techniques, and best practices for aspiring and experienced developers."
    )

    # (Assume you already have chapters, sections, items, and parts.)
    run_generate_contents_and_save_book(
        book_title=book_title,
        book_description=book_description,
        output_dir="my_full_book"
    )
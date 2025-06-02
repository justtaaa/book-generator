# AI Book Generator

This project automates the creation of a structured, multi‐chapter programming book using the OpenAI GPT API. It performs the following steps:
1. Generate an outline (chapters, sections, items).
2. Parse the outline into Python data structures.
3. Generate “parts” (subsections within each item) for every item.
4. Generate ~1000-word content for each part, passing previously-written snippets to minimize overlap.
5. Assemble everything into a single book.txt file, complete with:
    - Title page
    - Table of Contents
    - Full chapter/section/item/part content
    - Show progress in the terminal via a tqdm progress bar.

## Pre-requistes
1. `uv` [How to Install uv](https://docs.astral.sh/uv/)
2. **OpenAI API Key**
    - Sign up at [OpenAI](https://platform.openai.com/api-keys) and obtain an API Key

## Set-Up
1. Clone this repository
```bash
git clone https://github.com/jc2409/book-generator.git
```
2. Create a `.env` file in the project root, with the following content:
```ini
OPENAI_API_KEY=your_openai_api_key_here
```

## Usage

1. Run the `app.py`
```bash
uv run app.py
```
2. Enter the **title** of the book:
```output
Enter the book title: <Your Book Title>
```
3. Enter the **description** of the book:
```output
Enter the book description: <Your Book Description>
```

## Output

The generated response will be saved in the `book output` folder.
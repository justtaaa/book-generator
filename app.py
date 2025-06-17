import sys
sys.path.insert(0, './src/')

from generate_contents import run_generate_contents_and_save_book

def main():
    book_title = input("Enter the book title: ")
    book_description = input("Enter the book description: ")
    run_generate_contents_and_save_book(
        book_title=book_title,
        book_description=book_description
    )
    print(f"Book '{book_title}' contents generated successfully.")

if __name__ == "__main__":
    main()
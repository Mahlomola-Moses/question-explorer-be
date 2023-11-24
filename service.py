# services.py
class BookService:
    def __init__(self):
        # Sample data (in-memory database)
        self.books = [
            {"id": 1, "title": "Introduction to Python", "author": "John Doe"},
            {"id": 2, "title": "Web Development Basics", "author": "Jane Smith"}
        ]

    def get_all_books(self):
        return self.books

    def get_book_by_id(self, book_id):
        return next((b for b in self.books if b['id'] == book_id), None)

    def add_book(self, new_book):
        self.books.append(new_book)
        return new_book

    def update_book(self, book_id, updated_data):
        book = self.get_book_by_id(book_id)
        if book:
            book.update(updated_data)
            return book

    def delete_book(self, book_id):
        self.books = [b for b in self.books if b['id'] != book_id]

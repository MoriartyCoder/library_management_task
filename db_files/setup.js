db = db.getSiblingDB('lib_mgmt');

// Clear collections
db.book.deleteMany({});
db.genre.deleteMany({});
db.author.deleteMany({});
db.publisher.deleteMany({});
db.user.deleteMany({});

// Insert publishers
const publishers = db.publisher.insertMany([
  { _id: 1, name: "Penguin Books" },
  { _id: 2, name: "J.B. Lippincott & Co." },
  { _id: 3, name: "T. Egerton" },
  { _id: 4, name: "Secker and Warburg" },
  { _id: 5, name: "Penguin Life" }
]);

// Insert authors
const authors = db.author.insertMany([
  { _id: 1, name: "George Orwell", description: null },
  { _id: 2, name: "Harper Lee", description: null },
  { _id: 3, name: "Jane Austen", description: null },
  { _id: 4, name: "Francesc Miralles and Hector Garcia", description: null }
]);

// Insert genres
const genres = db.genre.insertMany([
  { _id: 1, name: "Fiction" },
  { _id: 2, name: "Non-Fiction" },
  { _id: 3, name: "Romance" },
  { _id: 4, name: "Satire" },
  { _id: 5, name: "Self Help" }
]);

// Insert users
const users = db.user.insertMany([
  { _id: 1, name: "Alice" },
  { _id: 2, name: "Bob" }
]);

// Insert books
const books = db.book.insertMany([
  { _id: 1, title: "1984", author_id: 1, publisher_id: 1, genre_id: 1, user_id: 1, borrow_date: new Date("2025-05-01"), due_date: new Date("2025-09-21") },
  { _id: 2, title: "To Kill a Mockingbird", author_id: 2, publisher_id: 2, genre_id: 1 },
  { _id: 3, title: "Pride and Prejudice", author_id: 3, publisher_id: 3, genre_id: 3 },
  { _id: 4, title: "Animal Farm", author_id: 1, publisher_id: 4, genre_id: 4 },
  { _id: 5, title: "Ikigai", author_id: 4, publisher_id: 5, genre_id: 5, user_id: 2, borrow_date: new Date("2025-05-01"), due_date: new Date("2025-09-21") }
]);

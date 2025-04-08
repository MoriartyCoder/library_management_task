DROP TABLE IF EXISTS Borrowed, Book, State, Genre, Author, Publisher, "User" CASCADE;

CREATE TABLE "User" (
    user_id SERIAL PRIMARY KEY,
    name TEXT
);

CREATE TABLE Book (
    book_id SERIAL PRIMARY KEY,
    title VARCHAR(75),
    borrowed_until DATE,
    state_id INT,
    genre_id INT,
    author_id INT,
    publisher_id INT
);

CREATE TABLE State (
    state_id SERIAL PRIMARY KEY,
    name VARCHAR(25)
);

CREATE TABLE Genre (
    genre_id SERIAL PRIMARY KEY,
    name VARCHAR(25)
);

CREATE TABLE Author (
    author_id SERIAL PRIMARY KEY,
    name VARCHAR(75),
    description TEXT
);

CREATE TABLE Publisher (
    publisher_id SERIAL PRIMARY KEY,
    name VARCHAR(50)
);

CREATE TABLE Borrowed (
    book_id INT REFERENCES Book(book_id),
    user_id INT REFERENCES "User"(user_id),
    borrow_date DATE,
    due_date DATE,
    PRIMARY KEY (book_id, user_id, borrow_date)
);


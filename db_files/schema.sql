DROP TABLE IF EXISTS Book, Genre, Author, Publisher, "User" CASCADE;

CREATE TABLE "User" (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(75)
);

CREATE TABLE Genre (
    genre_id SERIAL PRIMARY KEY,
    name VARCHAR(25) NOT NULL,
    description TEXT
);

CREATE TABLE Author (
    author_id SERIAL PRIMARY KEY,
    name VARCHAR(75) NOT NULL,
    description TEXT
);

CREATE TABLE Publisher (
    publisher_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT
);

CREATE TABLE Book (
    book_id SERIAL PRIMARY KEY,
    title VARCHAR(75) NOT NULL,
    user_id INT REFERENCES "User"(user_id),
    borrow_date DATE,
    due_date DATE,
    genre_id INT REFERENCES Genre(genre_id) NOT NULL,
    author_id INT REFERENCES Author(author_id) NOT NULL,
    publisher_id INT REFERENCES Publisher(publisher_id) NOT NULL,
    description TEXT
);

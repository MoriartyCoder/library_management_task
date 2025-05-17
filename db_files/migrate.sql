
TRUNCATE TABLE Borrowed, Book, State, Genre, Author, Publisher, "User";

INSERT INTO Publisher (name) VALUES
('Penguin Books'),
('J.B. Lippincott & Co.'),
('T. Egerton'),
('Secker and Warburg'),
('Penguin Life');

INSERT INTO Author (name, description) VALUES
('George Orwell', NULL),
('Harper Lee', NULL),
('Jane Austen', NULL),
('Francesc Miralles and Hector Garcia', NULL);

INSERT INTO Genre (name) VALUES
('Fiction'),       
('Non-Fiction'),   
('Romance'),       
('Satire'),       
('Self Help');

INSERT INTO State (name) VALUES
('Present'), ('Borrowed');

INSERT INTO "User" (name) VALUES
('Alice'),
('Bob');

INSERT INTO Book (title, author_id, publisher_id, genre_id, state_id) VALUES
('1984', 1, 1, 1, 1),
('To Kill a Mockingbird', 2, 2, 1, 1),
('Pride and Prejudice', 3, 3, 3, 1),
('Animal Farm', 1, 4, 4, 1),
('Ikigai', 4, 5, 5, 1);


-- INSERT INTO Borrowed (book_id, user_id, borrow_date, due_date) VALUES
-- (1, 1, '2024-03-01', '2024-03-21');

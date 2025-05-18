
TRUNCATE TABLE Book, Genre, Author, Publisher, "User";

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

INSERT INTO "User" (name) VALUES
('Alice'),
('Bob');

INSERT INTO Book (title, author_id, publisher_id, genre_id) VALUES
('1984', 1, 1, 1),
('To Kill a Mockingbird', 2, 2, 1),
('Pride and Prejudice', 3, 3, 3),
('Animal Farm', 1, 4, 4),
('Ikigai', 4, 5, 5);

UPDATE Book SET user_id = 1, borrow_date = '2025-05-01', due_date = '2025-09-21' WHERE book_id = 1;
UPDATE Book SET user_id = 2, borrow_date = '2025-05-01', due_date = '2025-09-21' WHERE book_id = 5;

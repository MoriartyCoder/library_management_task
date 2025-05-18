
function generate_page() {
    
}

window.onload = function () {
    Promise.all([
        fetch('/api/list').then(response => response.json()),
        fetch('/api/users').then(response => response.json())
    ]).then(([tableData, users]) => {

        const bookTable = document.getElementById('book-table');
        const borrowBookSelect = document.getElementById('borrowBookId');
        const borrowerBookSelect = document.getElementById('borrowerId');
        const returnBookSelect = document.getElementById('returnBookId');

        users.forEach(user => {
            const option = document.createElement('option');
            option.value = user.user_id;
            option.textContent = `${user.name}`;
            borrowerBookSelect.appendChild(option);
        });

        // Clear existing options
        borrowBookSelect.innerHTML = '<option value="">Select a Book</option>';
        returnBookSelect.innerHTML = '<option value="">Select a Book</option>';

        tableData.forEach(book => {
            const book_id = book["Book ID"];
            const title = book["Title"];
            const author = book["Author"];
            const author_id = book["author_id"];
            const publisher = book["Publisher"];
            const publisher_id = book["publisher_id"];
            const genre = book["Genre"];
            const genre_id = book["genre_id"];
            const borrower = book["Borrower"] || '';
            const user_id = book["user_id"];
            const borrowDate = book["Borrow Date"] || '';
            const returnDate = book["Return Date"] || '';
            const isBorrowed = borrowDate !== '';
            const state = isBorrowed ? 'Borrowed' : 'Present';

            // Create table row
            const row = document.createElement('tr');
            row.setAttribute('book-id', book_id);
            row.innerHTML = `<td>${book_id}</td>
                            <td><a href="viewer.html?table=Book&pk_name=book_id&pk_value=${book_id}" target="_blank">${title}</a></td>
                            <td><a href="viewer.html?table=Author&pk_name=author_id&pk_value=${author_id}" target="_blank">${author}</a></td>
                            <td><a href="viewer.html?table=Publisher&pk_name=publisher_id&pk_value=${publisher_id}" target="_blank">${publisher}</a></td>
                            <td><a href="viewer.html?table=Genre&pk_name=genre_id&pk_value=${genre_id}" target="_blank">${genre}</a></td>
                            <td>${borrower ? `<a href="viewer.html?table=User&pk_name=user_id&pk_value=${user_id}" target="_blank">${borrower}</a>` : ''}</td>
                            <td>${borrowDate}</td>
                            <td>${returnDate}</td>
                            <td>${state}</td>`;
            bookTable.appendChild(row);

            // Populate dropdowns
            const option = document.createElement('option');
            option.value = book_id;
            option.textContent = `${book_id} - ${title}`;

            if (!isBorrowed) {
                borrowBookSelect.appendChild(option);
            } else {
                returnBookSelect.appendChild(option);
            }
        });
    }).catch(error => {
        console.error('Error fetching or parsing data from server:', error);
    });
};

// Handle Borrow Form Submission
document.getElementById('borrowForm').addEventListener('submit', function (event) {
    event.preventDefault();
    const bookId = document.getElementById('borrowBookId').value;
    const borrowerId = document.getElementById('borrowerId').value;

    if (!bookId || !borrowerId) {
        alert('Please fill in all fields.');
        return;
    }

    // Confirmation Dialog
    if (!confirm(`Are you sure you want to borrow Book ID ${bookId}?`)) {
        return;
    }

    let url = '/api/borrow?' + new URLSearchParams({
        user_id: borrowerId, 
        book_id: bookId 
    }).toString();

    fetch(url, {
            method: 'POST'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error("Request failed");
            }
            return response.json();
        })
        .then(data => {
            location.reload();
        })
        .catch(error => {
            console.error('Error resetting borrowed books:', error);
            alert("An error occurred while resetting.");
        });
});

// Handle Return Form Submission
document.getElementById('returnForm').addEventListener('submit', function (event) {
    event.preventDefault();
    const bookId = document.getElementById('returnBookId').value;

    if (!bookId) {
        alert('Please select a book to return.');
        return;
    }

    // Confirmation Dialog
    if (!confirm(`Are you sure you want to return Book ID ${bookId}?`)) {
        return;
    }

    let url = '/api/return?' + new URLSearchParams({
        book_id: bookId 
    }).toString();

    fetch(url, {
            method: 'POST'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error("Request failed");
            }
            return response.json();
        })
        .then(data => {
            location.reload();
        })
        .catch(error => {
            console.error('Error resetting borrowed books:', error);
            alert("An error occurred while resetting.");
        });

});

// Clear borrowing data from DB
document.getElementById('clearDataBtn').addEventListener('click', function () {
    if (confirm('Are you sure you want to clear all borrowing data? This action cannot be undone.')) {
        fetch('/api/totalreset', {
            method: 'POST'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error("Request failed");
            }
            return response.json();
        })
        .then(data => {
            alert(data.message);
            location.reload(); // reload table data
        })
        .catch(error => {
            console.error('Error resetting borrowed books:', error);
            alert("An error occurred while resetting.");
        });
    }
});

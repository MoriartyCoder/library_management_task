window.onload = function () {
  const params = getQueryParams();
  const table = params["table"];
  const pk_name = params["pk_name"];
  const pk_value = params["pk_value"];

  if (table && pk_name && pk_value) {
    displayEntity(table, pk_name, pk_value);
  } else {
    document.getElementById("content").innerHTML = "<p>Invalid parameters.</p>";
  }
};

function generate_viewer_link(table, pk_name, pk_value, text) {
    return `<a href="viewer.html?table=${table}&pk_name=${pk_name}&pk_value=${pk_value}" target="_blank">${text}</a>`;
}

function attribute_name_to_text(attribute_name) {
    const mapping = {
        author_id: "Author",
        book_id: "Buch",
        borrow_date: "Borrow Date",
        due_date: "Due Date",
        genre_id: "Genre",
        publisher_id: "Publisher",
        title: "Title",
        user_id: "Borrower"
    }

    return mapping[attribute_name] || "UNKOWN";
}

function getQueryParams() {
  const params = {};
  window.location.search
    .substring(1)
    .split("&")
    .forEach((pair) => {
      const [key, value] = pair.split("=");
      if (key) {
        params[decodeURIComponent(key)] = decodeURIComponent(value || "");
      }
    });
  return params;
}

async function fetchGeminiDescription(entityName, table, pk_name, pk_value) {
  console.log("Fetching description for:", entityName);
  try {
    const response = await fetch(
      `/api/description?name=${encodeURIComponent(entityName)}`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    if (response.status === 400) {
      throw new Error("Invalid request. Entity name is missing.");
    } else if (response.status === 500) {
      throw new Error("Server error while fetching description.");
    } else if (!response.ok) {
      throw new Error("Unexpected error occurred.");
    }

    const data = await response.json();
    const descriptionMarkdown = data.description || "No description available.";
    const descriptionHTML = marked.parse(descriptionMarkdown);

    document.getElementById(
      "description"
    ).innerHTML = `<h2>Description</h2>${descriptionHTML}`;

    const url =
      "/api/update_description?" +
      new URLSearchParams({
        table: table,
        pk_name: pk_name,
        pk_value: pk_value,
      }).toString();

    const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(descriptionHTML)
    });

    const json = await res.json();
    if (json.success) alert('Saved!');
    else alert('Error: ' + json.error);

  } catch (error) {
    console.error("Error fetching description from Gemini API:", error);
    document.getElementById("description").innerHTML = `<p>${error.message}</p>`;
  }
}

async function displayEntity(table, pk_name, pk_value) {
  try {

    const urll =
      "/api/get_detail_view?" +
      new URLSearchParams({
        table: table,
        pk_name: pk_name,
        pk_value: pk_value,
      }).toString();

    const response = await fetch(urll);
    if (!response.ok) {
      throw new Error("TEST: Failed to fetch data from server.");
    }

    const data = await response.json();

    const entity = data[0];
    const entityType = table.charAt(0).toUpperCase() + table.slice(1);
    let htmlContent = `<h1>${entityType} Details</h1><ul>`;
    let entityName = "";

    for (const key in entity) {
        if (!entity.hasOwnProperty(key)) continue;

        const value = entity[key];
        if (value == null || key === 'description') continue;

        // Check if the current field is a foreign key (e.g., author_id)
        if (key.endsWith("_id") && key !== pk_name) {
            const relatedTable = key.replace("_id", "");
            const displayKey = get_display_name_key(relatedTable); // e.g. "Author" for author_id
            const displayName = entity[displayKey];

            const label = attribute_name_to_text(key);
            const link = generate_viewer_link(relatedTable, key, value, displayName ?? value);
            htmlContent += `<li><strong>${label}:</strong> ${link}</li>`;
        } else if(key[0] !== key[0].toUpperCase()) {
            console.log(key);
            const label = attribute_name_to_text(key);
            htmlContent += `<li><strong>${label}:</strong> ${value}</li>`;

            if (["name", "title"].includes(key.toLowerCase())) {
                entityName = value;
            }
        }
    }


    htmlContent += "</ul>";

    if (table.toLowerCase() === "book" && !entity["user_id"]) {
      htmlContent += `<p>This book is currently available for borrowing.</p>`;
    }

    htmlContent += `<a href="/" class="back-link">&larr; Back to Catalog</a>`;
    document.getElementById("content").innerHTML = htmlContent;

    if (entity.description == null) {
      fetchGeminiDescription(entityName, table, pk_name, pk_value);
    } else {
        document.getElementById("description").innerHTML = `<h2>Description</h2>${entity.description}`;
    }



  } catch (error) {
    console.error("Error displaying entity:", error);
    document.getElementById(
      "content"
    ).innerHTML = `<p>Error loading entity details.</p>`;
  }
}


function get_display_name_key(table) {
  const map = {
    author: "Author",
    genre: "Genre",
    publisher: "Publisher",
    user: "Borrower"
  };
  return map[table] || table;
}
document.addEventListener("DOMContentLoaded", function () {
  const searchForm = document.querySelector(".search-form");
  const searchInput = document.querySelector(".search-input");
  const searchResults = document.querySelector(".search-results");
  let timeoutId;

  // Function to hide search results
  const hideResults = () => {
    searchResults.innerHTML = "";
    searchResults.style.display = "none";
  };

  searchInput.addEventListener("input", function () {
    clearTimeout(timeoutId);
    const query = this.value.trim();

    if (query.length < 2) {
      hideResults();
      return;
    }

    timeoutId = setTimeout(() => {
      fetch(`/search?query=${encodeURIComponent(query)}`)
        .then((response) => {
          if (!response.ok) {
            throw new Error("Network response was not ok");
          }
          return response.json();
        })
        .then((data) => {
          searchResults.innerHTML = "";
          if (data.length > 0) {
            data.forEach((book) => {
              const item = document.createElement("div");
              item.className = "search-result-item";
              item.textContent = book.title;
              item.addEventListener("click", () => {
                searchInput.value = book.title;
                hideResults();
                searchForm.submit();
              });
              searchResults.appendChild(item);
            });
            searchResults.style.display = "block";
          } else {
            hideResults();
          }
        })
        .catch((error) => {
          console.error("Fetch error:", error);
          hideResults();
        });
    }, 300);
  });

  // Hide results when clicking outside
  document.addEventListener("click", function (e) {
    if (!searchForm.contains(e.target)) {
      hideResults();
    }
  });
}); 
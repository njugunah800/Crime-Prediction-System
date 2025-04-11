document.addEventListener("DOMContentLoaded", function () {
    document.querySelector("form").addEventListener("submit", function (e) {
        e.preventDefault(); // Prevent default form submission
        const formData = new FormData(this);

        fetch("/predict", {
            method: "POST",
            body: formData
        })
        .then(response => response.text())
        .then(data => {
            document.body.innerHTML = data; // Load result.html dynamically
        })
        .catch(error => console.error("Error:", error));
    });
});

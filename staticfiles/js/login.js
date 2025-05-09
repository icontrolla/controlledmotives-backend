document.getElementById("submit").addEventListener("click", function () {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();

    fetch('/profiles/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({
            username: username,
            password: password,
        }),
    })
    .then(response => {
        if (response.ok) {
            window.location.href = "/home/";
        } else {
            response.json().then(data => {
                alert(data.error || "Login failed");
            });
        }
    })
    .catch(error => {
        console.error("Error:", error);
        alert("An unexpected error occurred. Please try again.");
    });
});

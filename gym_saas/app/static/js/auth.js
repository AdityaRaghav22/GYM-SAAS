async function authFetch(url, options = {}) {
    options.credentials = "include"; // 🔥 REQUIRED for cookies

    let response = await fetch(url, options);

    // 🔁 If access token expired
    if (response.status === 401) {
        // Try refresh
        const refreshResponse = await fetch("/gym/refresh", {
            method: "POST",
            credentials: "include"
        });

        if (refreshResponse.ok) {
            // Retry original request
            response = await fetch(url, options);
        } else {
            // Refresh token expired → force logout
            window.location.href = "/gym/login";
            return;
        }
    }

    return response;
}

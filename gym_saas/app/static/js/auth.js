async function authFetch(url, options = {}) {
    // Always send cookies
    options = {
        ...options,
        credentials: "include"
    };

    let response;

    try {
        response = await fetch(url, options);
    } catch (err) {
        console.error("Network error:", err);
        throw err;
    }

    // If access token expired and this is NOT already a retry
    if (response.status === 401 && !options._retry && !url.includes("/gym/refresh")) {
        options._retry = true;

        const refreshResponse = await fetch("/gym/refresh", {
            method: "POST",
            credentials: "include"
        });

        if (refreshResponse.ok) {
            // Retry original request with new access token
            return fetch(url, options);
        }

        // Refresh token expired → force logout
        window.location.href = "/gym/login";
        return;
    }

    return response;
}

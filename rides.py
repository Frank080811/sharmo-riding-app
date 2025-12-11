// assets/js/rider.js
document.addEventListener("DOMContentLoaded", () => {
    console.log("🚀 Rider JS Loaded");

    // ---------------------------------------------------------
    // 🔐 LOGIN VALIDATION
    // ---------------------------------------------------------
    const userRaw = localStorage.getItem("swift_user");
    if (!userRaw) {
        window.location.href = "index.html";
        return;
    }

    const user = JSON.parse(userRaw);
    document.getElementById("rider-name").textContent = user.email.split("@")[0];

    const baseUrl = "https://sharmo-riding-app.onrender.com";

    // ---------------------------------------------------------
    // 🔓 LOGOUT BUTTON (FIXED)
    // ---------------------------------------------------------
    const logoutBtn = document.getElementById("btn-logout");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {
            console.log("Logging out...");
            localStorage.removeItem("swift_user");
            window.location.href = "index.html";
        });
    }

    // ---------------------------------------------------------
    // 🗺️ LEAFLET MAP (FULLY FIXED)
    // ---------------------------------------------------------
    let map = null;
    let marker = null;

    function initMap() {

        // Prevent Leaflet from creating multiple maps
        if (map !== null) return;

        map = L.map("map", { zoomControl: true });

        // Render fix for hidden parent elements
        setTimeout(() => {
            map.invalidateSize();
            map.setView([5.6037, -0.1870], 13); // Default Accra
        }, 200);

        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            maxZoom: 19,
            attribution: "© OpenStreetMap contributors"
        }).addTo(map);
    }

    initMap();

    // ---------------------------------------------------------
    // 📍 GEOLOCATION (FIXED + RETRY + FALLBACK)
    // ---------------------------------------------------------
    function requestLocation() {
        console.log("Requesting GPS...");

        if (!navigator.geolocation) {
            alert("Your device does not support location access.");
            return;
        }

        navigator.geolocation.getCurrentPosition(
            // SUCCESS
            (pos) => {
                console.log("GPS granted.");

                const lat = pos.coords.latitude;
                const lng = pos.coords.longitude;

                const pickupInput = document.getElementById("pickup");
                if (pickupInput) pickupInput.value = `${lat.toFixed(5)}, ${lng.toFixed(5)}`;

                if (!marker) {
                    marker = L.marker([lat, lng]).addTo(map);
                } else {
                    marker.setLatLng([lat, lng]);
                }

                map.setView([lat, lng], 15);
            },

            // ERROR
            (err) => {
                console.warn("GPS denied:", err.message);

                alert("Please enable location permission to use Shamor-Rides.");

                // Set default fallback view
                map.setView([5.6037, -0.1870], 13);
            },

            // OPTIONS
            { enableHighAccuracy: true, timeout: 8000 }
        );
    }

    // Initial GPS request
    setTimeout(requestLocation, 500);

    // Retry button
    const retryBtn = document.getElementById("enable-location");
    if (retryBtn) retryBtn.addEventListener("click", requestLocation);

    // ---------------------------------------------------------
    // 🚕 RIDE SUBMISSION
    // ---------------------------------------------------------
    const rideForm = document.getElementById("ride-form");

    rideForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const pickup = document.getElementById("pickup").value.trim();
        const dropoff = document.getElementById("dropoff").value.trim();
        const rideType = document.getElementById("ride-type").value;
        const payment = document.getElementById("payment-method").value;

        if (!pickup || !dropoff) {
            alert("Please fill pickup & dropoff.");
            return;
        }

        const res = await fetch(`${baseUrl}/rides`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: "Bearer " + user.token
            },
            body: JSON.stringify({
                pickup,
                dropoff,
                ride_type: rideType,
                payment_method: payment
            })
        });

        if (!res.ok) {
            const err = await res.json();
            alert("Ride failed: " + (err.detail || "Unknown error"));
            return;
        }

        alert("Ride created! A driver will be assigned.");
    });

});

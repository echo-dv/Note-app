(function () {
    "use strict";

    const menuButton = document.querySelector("[data-mobile-menu-button]");
    const nav = document.querySelector(".main-nav");

    if (menuButton && nav) {
        menuButton.addEventListener("click", function () {
            const opened = nav.classList.toggle("mobile-open");
            menuButton.setAttribute("aria-expanded", opened ? "true" : "false");
        });
    }

    const likeButton = document.querySelector("[data-like-button]");

    if (!likeButton) {
        return;
    }

    likeButton.addEventListener("click", async function () {
        if (likeButton.disabled) {
            return;
        }

        const url = likeButton.dataset.likeUrl;
        if (!url) {
            return;
        }

        likeButton.disabled = true;

        try {
            const response = await fetch(url, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCsrfToken(),
                    "X-Requested-With": "XMLHttpRequest",
                    "Accept": "application/json"
                },
                credentials: "same-origin"
            });

            if (!response.ok) {
                throw new Error("Request failed");
            }

            const data = await response.json();
            const label = likeButton.querySelector("[data-like-label]");
            const icon = likeButton.querySelector("[data-like-icon]");
            const count = likeButton.querySelector("[data-like-count]");

            if (data.liked) {
                likeButton.classList.add("is-liked");
                if (icon) icon.textContent = "♥";
                if (label) label.textContent = "Liked";
            } else {
                likeButton.classList.remove("is-liked");
                if (icon) icon.textContent = "♡";
                if (label) label.textContent = "Like";
            }

            if (count) {
                count.textContent = data.like_count;
            }
        } catch (error) {
            console.error(error);
        } finally {
            likeButton.disabled = false;
        }
    });

    function getCsrfToken() {
        const input = document.querySelector('input[name="csrfmiddlewaretoken"]');
        return input ? input.value : "";
    }
})();

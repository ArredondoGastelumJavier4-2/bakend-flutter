let lastScroll = 0;
const navbar = document.getElementById("mainNavbar");

window.addEventListener("scroll", () => {
    const currentScroll = window.pageYOffset;

    if (currentScroll <= 0) {
        navbar.classList.remove("nav-hide");
        navbar.classList.add("nav-show");
        return;
    }

    if (currentScroll > lastScroll) {
        // Bajando = ocultar navbar
        navbar.classList.add("nav-hide");
        navbar.classList.remove("nav-show");
    } else {
        // Subiendo = mostrar navbar
        navbar.classList.add("nav-show");
        navbar.classList.remove("nav-hide");
    }

    lastScroll = currentScroll;
});

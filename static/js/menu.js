document.addEventListener("DOMContentLoaded", function() {
    const nav = document.getElementById("menuPrincipal");
    const rol = localStorage.getItem("rol");

    if (rol === "admin") {
        nav.innerHTML += '<a href="admin.html" class="btn-login">Panel Admin</a>';
        nav.innerHTML += '<a href="#" onclick="logout()" class="btn-register">Salir</a>';
    } else if (rol) {
        nav.innerHTML += '<a href="#" onclick="logout()" class="btn-register">Salir</a>';
    } else {
        nav.innerHTML += '<a href="login.html" class="btn-login">Login</a>';
        nav.innerHTML += '<a href="register.html" class="btn-register">Register</a>';
    }
});

function logout() {
    localStorage.removeItem("rol");
    window.location.href = "../templates/login.html";
}
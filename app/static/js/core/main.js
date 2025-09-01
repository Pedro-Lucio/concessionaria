// Menu hambúrguer
document.getElementById('icone-menu').addEventListener('click', function () {
    document.getElementById('lista').classList.toggle('active');
});

// Fechar menu ao clicar em um item
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', function () {
        document.getElementById('lista').classList.remove('active');
    });
});

// Efeito de scroll no header
window.addEventListener('scroll', function () {
    const header = document.getElementById('header');
    if (window.scrollY > 50) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }
});

// Fechar dropdown ao clicar fora
document.addEventListener('click', function (e) {
    const perfilContainer = document.querySelector('.perfil-container');
    const dropdown = document.querySelector('.dropdown-perfil');
    if (perfilContainer && dropdown && !perfilContainer.contains(e.target)) {
        dropdown.style.opacity = '0';
        dropdown.style.visibility = 'hidden';
        dropdown.style.transform = 'translateY(-10px)';
    }
});
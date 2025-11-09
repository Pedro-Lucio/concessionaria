// Menu hambúrguer
// document.getElementById('icone-menu').addEventListener('click', function () {
//     document.getElementById('lista').classList.toggle('active');
// });

// Fechar menu ao clicar em um item
// document.querySelectorAll('.nav-link').forEach(link => {
//     link.addEventListener('click', function () {
//         document.getElementById('lista').classList.remove('active');
//     });
// });

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

// Para as mensagens que aparecem na tela
document.addEventListener('DOMContentLoaded', function () {
    const alerts = document.querySelectorAll('.messages .alert');

    alerts.forEach(function (el) {
        const duration = parseInt(el.dataset.duration, 10) || 5000;
        const closeBtn = el.querySelector('.msg-close');
        const timerBar = el.querySelector('.timer-bar');

        // animação da barra
        if (timerBar) {
            setTimeout(() => { timerBar.style.transition = `width ${duration}ms linear`; timerBar.style.width = '0%'; }, 10);
        }

        // click no X
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                el.classList.add('fade-out');
                setTimeout(() => el.remove(), 280);
            });
        }

        // remoção automática
        setTimeout(() => {
            if (!document.contains(el)) return;
            el.classList.add('fade-out');
            setTimeout(() => { if (el.parentNode) el.remove(); }, 280);
        }, duration);
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const toggle = document.querySelector(".submenu-toggle");
    const submenu = document.querySelector(".submenu-gerencia");

    if (toggle && submenu) {
        toggle.addEventListener("click", function (e) {
            e.preventDefault();
            submenu.style.display =
                submenu.style.display === "flex" ? "none" : "flex";
        });
    }
});
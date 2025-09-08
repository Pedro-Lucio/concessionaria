document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('filter-form');
    const resetBtn = document.getElementById('reset-filters');
    const carrosCards = document.querySelectorAll('.carro-card');
    const filterInputs = document.querySelectorAll('#filter-form input');

    // Pega valores de checkboxes
    function getCheckedValues(name) {
        return Array.from(document.querySelectorAll(`input[name="${name}"]:checked`))
            .map(cb => cb.value.trim().toLowerCase());
    }

    function aplicarFiltros() {
        const marcas = getCheckedValues('marca');
        const cores = getCheckedValues('cor');
        const tipos = getCheckedValues('tipo');
        const cambios = getCheckedValues('cambio');
        const combustiveis = getCheckedValues('combustivel');

        let valorMin = parseFloat(document.getElementById('valorMin').value);
        let valorMax = parseFloat(document.getElementById('valorMax').value);
        let anoMin = parseInt(document.getElementById('ano_min').value);
        let anoMax = parseInt(document.getElementById('ano_max').value);
        let kmMax = parseInt(document.getElementById('km_max').value);

        // Tratamento de valores inválidos
        if (isNaN(valorMin) || valorMin < 5000) valorMin = 5000;
        if (isNaN(valorMax) || valorMax > 200000) valorMax = 200000;
        if (isNaN(anoMin) || anoMin < 1990) anoMin = 1990;
        if (isNaN(anoMax) || anoMax > new Date().getFullYear()) anoMax = new Date().getFullYear();
        if (isNaN(kmMax) || kmMax < 0) kmMax = Infinity;

        carrosCards.forEach(card => {
            const marca = card.dataset.marca.trim().toLowerCase();
            const cor = card.dataset.cor.trim().toLowerCase();
            const tipo = card.dataset.tipo.trim().toLowerCase();
            const cambio = card.dataset.cambio.trim().toLowerCase();
            const combustivel = card.dataset.combustivel.trim().toLowerCase();
            const valor = parseFloat(card.dataset.valor);
            const ano = parseInt(card.dataset.ano);
            const km = parseInt(card.dataset.km);

            const match =
                (marcas.length === 0 || marcas.includes(marca)) &&
                (cores.length === 0 || cores.includes(cor)) &&
                (tipos.length === 0 || tipos.includes(tipo)) &&
                (cambios.length === 0 || cambios.includes(cambio)) &&
                (combustiveis.length === 0 || combustiveis.includes(combustivel)) &&
                valor >= valorMin && valor <= valorMax &&
                ano >= anoMin && ano <= anoMax &&
                km <= kmMax;

            card.style.display = match ? 'block' : 'none';
        });
    }

    // Filtros automáticos
    filterInputs.forEach(input => {
        input.addEventListener('change', aplicarFiltros);
        if (input.type === 'number') {
            input.addEventListener('keyup', function() {
                clearTimeout(this.timer);
                this.timer = setTimeout(aplicarFiltros, 500);
            });
        }
    });

    // Reset
    resetBtn.addEventListener('click', function() {
        form.reset();
        document.getElementById('valorMin').value = 20000;
        document.getElementById('valorMax').value = 200000;
        aplicarFiltros();
    });

    // Parâmetros da URL
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.toString()) {
        urlParams.forEach((value, key) => {
            if (['marca','cor','tipo','cambio','combustivel'].includes(key)) {
                value.split(',').forEach(val => {
                    const checkbox = document.querySelector(`input[name="${key}"][value="${val}"]`);
                    if (checkbox) checkbox.checked = true;
                });
            } else {
                const el = document.getElementById(key);
                if (el) el.value = value;
            }
        });
        aplicarFiltros();
    }
});

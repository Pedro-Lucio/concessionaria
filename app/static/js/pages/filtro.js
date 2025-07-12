document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('filter-form');
    const resetBtn = document.getElementById('reset-filters');
    const carrosCards = document.querySelectorAll('.carro-card');
    const filterInputs = document.querySelectorAll('#filter-form input');
    
    // Função para obter valores selecionados dos checkboxes
    function getCheckedValues(name) {
        const checkboxes = document.querySelectorAll(`input[name="${name}"]:checked`);
        return Array.from(checkboxes).map(cb => cb.value.toLowerCase());
    }
    
    // Função para aplicar os filtros
    function aplicarFiltros() {
        const marcasSelecionadas = getCheckedValues('marca');
        const coresSelecionadas = getCheckedValues('cor');
        const tiposSelecionados = getCheckedValues('tipo');
        const cambiosSelecionados = getCheckedValues('cambio');
        const combustiveisSelecionados = getCheckedValues('combustivel');
        
        const valorMin = parseFloat(document.getElementById('valor_min').value) || 0;
        const valorMax = parseFloat(document.getElementById('valor_max').value) || Infinity;
        const anoMin = parseInt(document.getElementById('ano_min').value) || 0;
        const anoMax = parseInt(document.getElementById('ano_max').value) || Infinity;
        const kmMax = parseInt(document.getElementById('km_max').value) || Infinity;
        
        carrosCards.forEach(card => {
            const cardMarca = card.dataset.marca.toLowerCase();
            const cardCor = card.dataset.cor.toLowerCase();
            const cardTipo = card.dataset.tipo.toLowerCase();
            const cardCambio = card.dataset.cambio.toLowerCase();
            const cardCombustivel = card.dataset.combustivel.toLowerCase();
            const cardValor = parseFloat(card.dataset.valor);
            const cardAno = parseInt(card.dataset.ano);
            const cardKm = parseInt(card.dataset.km);
            
            // Verificar seleções (se nenhum checkbox foi marcado, mostra todos)
            const marcaMatch = marcasSelecionadas.length === 0 || marcasSelecionadas.includes(cardMarca);
            const corMatch = coresSelecionadas.length === 0 || coresSelecionadas.includes(cardCor);
            const tipoMatch = tiposSelecionados.length === 0 || tiposSelecionados.includes(cardTipo);
            const cambioMatch = cambiosSelecionados.length === 0 || cambiosSelecionados.includes(cardCambio);
            const combustivelMatch = combustiveisSelecionados.length === 0 || combustiveisSelecionados.includes(cardCombustivel);
            
            // Verificar faixas
            const valorMatch = cardValor >= valorMin && cardValor <= valorMax;
            const anoMatch = cardAno >= anoMin && cardAno <= anoMax;
            const kmMatch = cardKm <= kmMax;
            
            if (marcaMatch && corMatch && tipoMatch && cambioMatch && combustivelMatch && 
                valorMatch && anoMatch && kmMatch) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    }
    
    // Aplicar filtros automaticamente quando qualquer input muda
    filterInputs.forEach(input => {
        input.addEventListener('change', aplicarFiltros);
        if (input.type === 'number') {
            input.addEventListener('keyup', function(e) {
                // Atraso para evitar filtragem a cada tecla pressionada
                clearTimeout(this.timer);
                this.timer = setTimeout(aplicarFiltros, 500);
            });
        }
    });
    
    // Evento de reset dos filtros
    resetBtn.addEventListener('click', function() {
        // Resetar todos os inputs
        form.reset();
        // Aplicar filtros para mostrar todos os carros
        aplicarFiltros();
    });
    
    // Aplicar filtros ao carregar a página se houver parâmetros na URL
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.toString()) {
        // Preencher os campos do formulário com os parâmetros da URL
        urlParams.forEach((value, key) => {
            if (key === 'marca' || key === 'cor' || key === 'tipo' || key === 'cambio' || key === 'combustivel') {
                // Para checkboxes, marcar os valores separados por vírgula
                const values = value.split(',');
                values.forEach(val => {
                    const checkbox = document.querySelector(`input[name="${key}"][value="${val}"]`);
                    if (checkbox) checkbox.checked = true;
                });
            } else {
                const element = document.getElementById(key);
                if (element) element.value = value;
            }
        });
        
        // Aplicar os filtros
        aplicarFiltros();
    }
});
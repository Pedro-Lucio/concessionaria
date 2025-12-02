// // Interatividade com o Price Ranger
// window.onload = function () {
//     slideMin();
//     slideMax();
// };

// const minVal = document.querySelector(".valorMin");
// const maxVal = document.querySelector(".valorMax");
// const priceInputMin = document.querySelector(".min-input");
// const priceInputMax = document.querySelector(".max-input");
// const minTooltip = document.querySelector(".min-tooltip");
// const maxTooltip = document.querySelector(".max-tooltip");
// const minGap = 0;
// const range = document.querySelector(".slider-track");
// const sliderMinValue = parseInt(minVal.min);
// const sliderMaxValue = parseInt(maxVal.max);

// function slideMin() {
//     let gap = parseInt(maxVal.value) - parseInt(minVal.value);
//     if (gap <= minGap) {
//         minVal.value = parseInt(maxVal.value) - minGap;
//     }
//     minTooltip.innerHTML = "$" + minVal.value;
//     priceInputMin.value = minVal.value;
//     setArea();
// }

// function slideMax() {
//     let gap = parseInt(maxVal.value) - parseInt(minVal.value);
//     if (gap <= minGap) {
//         maxVal.value = parseInt(minVal.value) + minGap;
//     }
//     maxTooltip.innerHTML = "$" + maxVal.value;
//     priceInputMax.value = maxVal.value;
//     setArea()
// }

// function setArea() {
//     // range.style.left = `${((minVal.value - sliderMinValue) / (sliderMaxValue - sliderMinValue)) * 100}%`;
//     range.style.left = (minVal.value / sliderMaxValue) * 100 + "%";
//     minTooltip.style.left = (minVal.value / sliderMaxValue) * 100 + "%";

//     // range.style.right = `${100 - ((maxVal.value - sliderMinValue) / (sliderMaxValue - sliderMinValue)) * 100}%`;
//     range.style.right = 100 - (maxVal.value / sliderMaxValue) * 100 + "%";
//     maxTooltip.style.right = 100 - (maxVal.value / sliderMaxValue) * 100 + "%";
// }

// function setMinInput() {
//     let minPrice = parseInt(priceInputMin.value);
//     if (minPrice < sliderMinValue) {
//         priceInputMin.value = sliderMinValue;
//     }
//     minVal.value = priceInputMin.value;
//     slideMin();
// }

// function setMaxInput() {
//     let maxPrice = parseInt(priceInputMax.value);
//     if (maxPrice > sliderMaxValue) {
//         priceInputMax.value = sliderMaxValue;
//     }
//     maxVal.value = priceInputMax.value;
//     slideMax();
// }















// // Interatividade com os filtros
// document.addEventListener('DOMContentLoaded', function () {
//     const form = document.getElementById('filter-form');
//     const resetBtn = document.getElementById('reset-filters');
//     const carrosCards = document.querySelectorAll('.carro-card');
//     const filterInputs = document.querySelectorAll('#filter-form input');

//     // Função para obter valores selecionados dos checkboxes
//     function getCheckedValues(name) {
//         const checkboxes = document.querySelectorAll(`input[name="${name}"]:checked`);
//         return Array.from(checkboxes).map(cb => cb.value.toLowerCase());
//     }

//     // Função para aplicar os filtros
//     function aplicarFiltros() {
//         const marcasSelecionadas = getCheckedValues('marca');
//         const coresSelecionadas = getCheckedValues('cor');
//         const tiposSelecionados = getCheckedValues('tipo');
//         const cambiosSelecionados = getCheckedValues('cambio');
//         const combustiveisSelecionados = getCheckedValues('combustivel');

//         const valorMin = parseFloat(document.getElementById('valorMin').value) || 0;
//         const valorMax = parseFloat(document.getElementById('valorMax').value) || Infinity;
//         const anoMin = parseInt(document.getElementById('ano_min').value) || 0;
//         const anoMax = parseInt(document.getElementById('ano_max').value) || Infinity;
//         const kmMax = parseInt(document.getElementById('km_max').value) || Infinity;

//         carrosCards.forEach(card => {
//             const cardMarca = card.dataset.marca.toLowerCase();
//             const cardCor = card.dataset.cor.toLowerCase();
//             const cardTipo = card.dataset.tipo.toLowerCase();
//             const cardCambio = card.dataset.cambio.toLowerCase();
//             const cardCombustivel = card.dataset.combustivel.toLowerCase();
//             const cardValor = parseFloat(card.dataset.valor);
//             const cardAno = parseInt(card.dataset.ano);
//             const cardKm = parseInt(card.dataset.km);

//             // Verificar seleções (se nenhum checkbox foi marcado, mostra todos)
//             const marcaMatch = marcasSelecionadas.length === 0 || marcasSelecionadas.includes(cardMarca);
//             const corMatch = coresSelecionadas.length === 0 || coresSelecionadas.includes(cardCor);
//             const tipoMatch = tiposSelecionados.length === 0 || tiposSelecionados.includes(cardTipo);
//             const cambioMatch = cambiosSelecionados.length === 0 || cambiosSelecionados.includes(cardCambio);
//             const combustivelMatch = combustiveisSelecionados.length === 0 || combustiveisSelecionados.includes(cardCombustivel);

//             // Verificar faixas
//             const valorMatch = cardValor >= valorMin && cardValor <= valorMax;
//             const anoMatch = cardAno >= anoMin && cardAno <= anoMax;
//             const kmMatch = cardKm <= kmMax;

//             if (marcaMatch && corMatch && tipoMatch && cambioMatch && combustivelMatch &&
//                 valorMatch && anoMatch && kmMatch) {
//                 card.style.display = 'block';
//             } else {
//                 card.style.display = 'none';
//             }
//         });
//     }

//     // Aplicar filtros automaticamente quando qualquer input muda
//     filterInputs.forEach(input => {
//         input.addEventListener('change', aplicarFiltros);
//         if (input.type === 'number') {
//             input.addEventListener('keyup', function (e) {
//                 // Atraso para evitar filtragem a cada tecla pressionada
//                 clearTimeout(this.timer);
//                 this.timer = setTimeout(aplicarFiltros, 500);
//             });
//         }
//     });

//     // Evento de reset dos filtros
//     resetBtn.addEventListener('click', function () {
//         // Resetar todos os inputs
//         form.reset();
//         // Aplicar filtros para mostrar todos os carros
//         aplicarFiltros();
//     });

//     // Aplicar filtros ao carregar a página se houver parâmetros na URL
//     const urlParams = new URLSearchParams(window.location.search);
//     if (urlParams.toString()) {
//         // Preencher os campos do formulário com os parâmetros da URL
//         urlParams.forEach((value, key) => {
//             if (key === 'marca' || key === 'cor' || key === 'tipo' || key === 'cambio' || key === 'combustivel') {
//                 // Para checkboxes, marcar os valores separados por vírgula
//                 const values = value.split(',');
//                 values.forEach(val => {
//                     const checkbox = document.querySelector(`input[name="${key}"][value="${val}"]`);
//                     if (checkbox) checkbox.checked = true;
//                 });
//             } else {
//                 const element = document.getElementById(key);
//                 if (element) element.value = value;
//             }
//         });

//         // Aplicar os filtros
//         aplicarFiltros();
//     }
// });







// Comparação entre dois veículos
document.addEventListener("DOMContentLoaded", function () {
    const toggleCompareBtn = document.querySelector(".btn-outline-primary"); // botão lateral
    const compareButtons = document.querySelectorAll(".btn-comparar-card");
    let compareMode = false;
    let selectedCars = [];

    // Função para redirecionar quando 2 carros forem escolhidos
    function goToCompare() {
        if (selectedCars.length === 2) {
            const url = `/comparar?carro1=${selectedCars[0]}&carro2=${selectedCars[1]}`;
            window.location.href = url;
        }
    }

    // Ativa/desativa modo de comparação
    toggleCompareBtn.addEventListener("click", () => {
        compareMode = !compareMode;
        selectedCars = []; // reseta seleção
        compareButtons.forEach(btn => {
            btn.classList.toggle("d-none", !compareMode);
            btn.classList.remove("active"); // remove destaque visual
        });
        toggleCompareBtn.textContent = compareMode ? "Cancelar Comparação" : "Comparar";

        if (compareMode) {
            const modal = new bootstrap.Modal(document.getElementById("compararModal"));
            modal.show();}
    });

    // Clique nos botões dos cards
    compareButtons.forEach(btn => {
        btn.addEventListener("click", function (e) {
            e.preventDefault();
            const carId = this.dataset.id;

            // Seleção/desmarcação
            if (selectedCars.includes(carId)) {
                selectedCars = selectedCars.filter(id => id !== carId);
                this.classList.remove("active");
            } else {
                if (selectedCars.length < 2) {
                    selectedCars.push(carId);
                    this.classList.add("active");
                }
            }

            // Se já tiver 2 → vai para página de comparação
            if (selectedCars.length === 2) {
                goToCompare();
            }
        });
    });
});

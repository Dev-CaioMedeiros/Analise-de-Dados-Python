document.addEventListener('DOMContentLoaded', function () {
    const radiopadrao = document.querySelector('input[value="padrao"]');
    const radioIntervalo = document.querySelector('input[value="intervalo"]');
    const filtropadrao = document.getElementById('filtro-padrao');
    const filtroIntervalo = document.getElementById('filtro-intervalo');

    function atualizarVisibilidade() {
        if (radiopadrao.checked) {
            filtropadrao.style.display = 'block';
            filtroIntervalo.style.display = 'none';
        } else {
            filtropadrao.style.display = 'none';
            filtroIntervalo.style.display = 'block';
        }
    }

    radiopadrao.addEventListener('change', atualizarVisibilidade);
    radioIntervalo.addEventListener('change', atualizarVisibilidade);

    atualizarVisibilidade();
});

const img = document.getElementById('grafico-img');
const loader = document.getElementById('loader');
const container = document.getElementById('grafico-container');

img.onload = function() {
    loader.style.display = 'none';
    container.style.display = 'block';
};

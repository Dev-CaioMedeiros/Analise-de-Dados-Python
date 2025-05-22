function toggleFilters() {
    const tipo = document.querySelector('select[name="tipo_filtro"]').value;
    document.getElementById("padrao-filtros").style.display = tipo === "padrao" ? "block" : "none";
    document.getElementById("intervalo-filtros").style.display = tipo === "intervalo" ? "block" : "none";
}

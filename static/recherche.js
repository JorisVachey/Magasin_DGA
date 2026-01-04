function recherche() {
    const form = document.getElementById('search-form');
    if (form) {
        form.submit();
    }
}
window.addEventListener('DOMContentLoaded', (event) => {
    const input = document.getElementById('search-input');
    if (input) {
        const val = input.value;
        input.focus();
        input.value = '';
        input.value = val;
    }
});

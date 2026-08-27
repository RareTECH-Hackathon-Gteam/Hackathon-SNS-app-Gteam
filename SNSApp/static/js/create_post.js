const textarea = document.getElementById('post-content');
const charCount = document.getElementById('char-count');

textarea.addEventListener('input', () => {
    const currentLength = textarea.value.length;
    charCount.textContent = `${currentLength}/140`;
});

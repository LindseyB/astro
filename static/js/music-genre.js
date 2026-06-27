// Music genre selection functionality

document.addEventListener('DOMContentLoaded', function() {
    const genreSelect = document.getElementById('music_genre');
    if (!genreSelect) return;

    genreSelect.addEventListener('change', toggleOtherGenre);
    toggleOtherGenre();
});

// Toggle the "Other" genre input field
function toggleOtherGenre() {
    const genreSelect = document.getElementById('music_genre');
    const otherGenreDiv = document.getElementById('other_genre_div');
    if (!genreSelect || !otherGenreDiv) return;
    
    if (genreSelect.value === 'other') {
        otherGenreDiv.style.display = 'block';
    } else {
        otherGenreDiv.style.display = 'none';
        // Clear the other genre input when hiding
        const otherGenreInput = document.getElementById('other_genre');
        if (otherGenreInput) {
            otherGenreInput.value = '';
        }
    }
}

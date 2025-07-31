// Music genre selection functionality

// Toggle the "Other" genre input field
function toggleOtherGenre() {
    const genreSelect = document.getElementById('music_genre');
    const otherGenreDiv = document.getElementById('other_genre_div');
    
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

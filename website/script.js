let http = new XMLHttpRequest();

http.open("GET", "songJSON.json", true);
http.send();

http.onload = function () {
    if (this.readyState == 4 && this.status == 200) {
        let song = JSON.parse(this.responseText);

        // Clean lyrics
        let lyricsStartIndex = song.lyrics.indexOf("[");
        let cleanedLyrics =
            lyricsStartIndex !== -1
                ? song.lyrics.substring(lyricsStartIndex).trim()
                : song.lyrics;

        let formattedLyrics = cleanedLyrics.replace(/\n/g, "<br>");

        let output = `
            <div class="song">
                <img src="${song.songArtImagePath}" alt="Cover of ${song.title}" class="cover">
                <p class="title">${song.title}</p>
                <p class="artist">${song.artist}</p>
                <p class="lyrics">${formattedLyrics}</p>
            </div>`;

        document.querySelector(".songs").innerHTML = output;

        // Background color
        const dominantColor = song.dominantColor;
        document.body.style.backgroundColor = `rgb(${dominantColor[0]}, ${dominantColor[1]}, ${dominantColor[2]})`;

        // Contrast text color
        document.body.style.color = getContrastYIQ(dominantColor);
    }
};

// Contrast helper
function getContrastYIQ(rgb) {
    const [r, g, b] = rgb;
    const yiq = (r * 299 + g * 587 + b * 114) / 1000;
    return yiq >= 128 ? "#000" : "#fff";
}

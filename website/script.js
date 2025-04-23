let http = new XMLHttpRequest();

http.open("GET", "songJSON.json", true);
http.send();

http.onload = function () {
    if (this.readyState == 4 && this.status == 200) {
        let song = JSON.parse(this.responseText);

        // Remove everything before and including the first occurrence of "["
        let lyricsStartIndex = song.lyrics.indexOf("[");
        let cleanedLyrics = lyricsStartIndex !== -1 ? song.lyrics.substring(lyricsStartIndex).trim() : song.lyrics;

        // Replace \n with <br> for line breaks
        let formattedLyrics = cleanedLyrics.replace(/\n/g, "<br>");

        let output = `
            <div class="song">
                <img src="${song.songArtImagePath}" alt="Cover of ${song.title}" class="cover">
                <iframe class="embed" src="${song.embed}" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>
                <p class="title">${song.title}</p>
                <p class="artist">${song.artist}</p>
                <p class="lyrics">${formattedLyrics}</p>
            </div>`;

        document.querySelector(".songs").innerHTML = output;

        // Display the latest 5 songs
        let latestSongsOutput = '<div style="margin: 20px 0;"><h3>Latest Songs</h3></div>';

        song.latestSongs.forEach((embedLink) => {
            latestSongsOutput += `
                <iframe class="embed" src="${embedLink}" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>
            `;
        });
        document.querySelector(".latest-songs").innerHTML = latestSongsOutput;

        // Set the background color dynamically
        const dominantColor = song.dominantColor;
        document.body.style.backgroundColor = `rgb(${dominantColor[0]}, ${dominantColor[1]}, ${dominantColor[2]})`;

        // Adjust text color for readability
        const textColor = getContrastYIQ(dominantColor);
        document.body.style.color = textColor;
    }
};

// Function to determine text color (black or white) based on background brightness
function getContrastYIQ(rgb) {
    const [r, g, b] = rgb;
    const yiq = (r * 299 + g * 587 + b * 114) / 1000; // Brightness formula
    return yiq >= 128 ? "#000" : "#fff"; // Return black for bright backgrounds, white for dark
}
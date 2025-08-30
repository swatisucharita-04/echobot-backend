document.addEventListener("DOMContentLoaded", () => {
  const responseAudio = document.getElementById("responseAudio");
  let audioQueue = [];

  window.playAudioChunk = (base64Chunk) => {
    const byteCharacters = atob(base64Chunk);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);

    audioQueue.push(byteArray);
    if (audioQueue.length === 1) playNextChunk();
  };

  const playNextChunk = () => {
    if (!audioQueue.length) return;

    const chunk = audioQueue[0];
    const blob = new Blob([chunk], { type: 'audio/mp3' }); // <-- MP3 type
    const url = URL.createObjectURL(blob);

    responseAudio.src = url;
    responseAudio.play();

    responseAudio.onended = () => {
      audioQueue.shift();
      URL.revokeObjectURL(url); // free memory
      if (audioQueue.length > 0) playNextChunk();
    };
  };
});

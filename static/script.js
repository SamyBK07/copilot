const output = document.getElementById("output");
const micButton = document.getElementById("micButton");

function speak(text) {
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "fr-FR";
  speechSynthesis.speak(utterance);
}

async function sendMessage(message) {
  output.innerHTML += `<p><b>Toi :</b> ${message}</p>`;
  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });

    const data = await response.json();

    if (data.response) {
      output.innerHTML += `<p><b>IA :</b> ${data.response}</p>`;
      speak(data.response);
    } else {
      output.innerHTML += `<p><b>Erreur :</b> ${data.error}</p>`;
    }
  } catch (err) {
    output.innerHTML += `<p><b>Erreur de connexion :</b> ${err.message}</p>`;
  }
}

// 🎤 Enregistrement vocal (compatible Chromebook)
micButton.addEventListener("click", async () => {
  const recognition = new (window.SpeechRecognition ||
    window.webkitSpeechRecognition)();

  recognition.lang = "fr-FR";
  recognition.start();

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    sendMessage(transcript);
  };

  recognition.onerror = (event) => {
    output.innerHTML += `<p><b>Erreur micro :</b> ${event.error}</p>`;
  };
});

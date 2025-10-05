const output = document.getElementById("output");
const micButton = document.getElementById("micButton");
const voiceSelect = document.getElementById("voiceSelect");

let mediaRecorder;
let audioChunks = [];

// Remplir les voix disponibles
let voices = [];
function populateVoices() {
  voices = speechSynthesis.getVoices();
  voiceSelect.innerHTML = "";
  voices.forEach((v, i) => {
    const option = document.createElement("option");
    option.value = i;
    option.textContent = `${v.name} (${v.lang})`;
    voiceSelect.appendChild(option);
  });
}
speechSynthesis.onvoiceschanged = populateVoices;
populateVoices();

function speak(text) {
  const utterance = new SpeechSynthesisUtterance(text);
  const selectedVoiceIndex = voiceSelect.value || 0;
  utterance.voice = voices[selectedVoiceIndex];
  utterance.lang = voices[selectedVoiceIndex]?.lang || "fr-FR";
  speechSynthesis.speak(utterance);
}

// --- Envoi d'un message texte ou transcription ---
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
    output.innerHTML += `<p><b>Erreur réseau :</b> ${err.message}</p>`;
  }
}

// --- Enregistrement audio via MediaRecorder ---
micButton.addEventListener("click", async () => {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    alert("Microphone non supporté");
    return;
  }

  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream);
  audioChunks = [];

  mediaRecorder.ondataavailable = e => audioChunks.push(e.data);

  mediaRecorder.onstop = async () => {
    const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
    const formData = new FormData();
    formData.append("audio", audioBlob, "audio.webm");

    // Appel backend pour transcription
    const res = await fetch("/transcribe", {
      method: "POST",
      body: formData
    });
    const data = await res.json();
    if (data.transcript) {
      sendMessage(data.transcript);
    } else {
      output.innerHTML += `<p><b>Erreur transcription :</b> ${data.error}</p>`;
    }
  };

  mediaRecorder.start();
  micButton.textContent = "🎧 Enregistrement... (clic pour arrêter)";
  micButton.onclick = () => {
    mediaRecorder.stop();
    micButton.textContent = "🎙️ Parler";
    micButton.onclick = arguments.callee; // remet l’événement
  };
});

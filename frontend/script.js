
const mic = document.getElementById('micIcon');
const response = document.getElementById('response');
const backendBtn = document.getElementById('backendListenBtn');

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();
recognition.lang = 'en-US';

mic.addEventListener('click', () => {
  speak("I'm listening. Please say something.");
  recognition.start();
  mic.classList.add('listening');
});

recognition.onresult = function(event) {
  const spoken = event.results[0][0].transcript;
  response.textContent = "You said: " + spoken;
  mic.classList.remove('listening');

  // Send to FastAPI backend
  fetch('http://127.0.0.1:8000/process-text', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ text: spoken })
  })
  .then(res => res.json())
  .then(data => {
    if (data.result) {
      response.textContent = `JARVIS: ${JSON.stringify(data.result)}`;
      speak(`Here's what I found: ${data.result}`);
    } else {
      response.textContent = "JARVIS couldn't process the intent.";
      speak("I couldn't process that. Try again.");
    }
  })
  .catch(error => {
    console.error("Error contacting API:", error);
    response.textContent = "⚠️ Error connecting to server.";
    speak("There was an error reaching the server.");
  });
};

recognition.onend = () => {
  mic.classList.remove('listening');
};

backendBtn.addEventListener('click', () => {
  response.textContent = "JARVIS (backend) is listening...";
  speak("Listening from backend. Please speak.");

  fetch('http://127.0.0.1:8000/listen')
    .then(res => res.json())
    .then(data => {
      if (data.recognized_text) {
        response.textContent = `You said (backend): ${data.recognized_text}`;
        speak(`You said: ${data.recognized_text}`);
      }

      if (data.result) {
        response.textContent += `\nJARVIS: ${JSON.stringify(data.result)}`;
        speak(`Here's what I found: ${data.result}`);
      }

      if (data.error) {
        response.textContent = `⚠️ ${data.error}`;
        speak("Backend could not understand your voice.");
      }
    })
    .catch(err => {
      console.error("Error from backend listener:", err);
      response.textContent = "⚠️ Error reaching backend listener.";
      speak("There was a backend error.");
    });
});

function speak(text) {
  const say = new SpeechSynthesisUtterance(text);
  window.speechSynthesis.speak(say);
}

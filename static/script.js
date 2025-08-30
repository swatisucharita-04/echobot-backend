// static/script.js
document.addEventListener("DOMContentLoaded", () => {
  const recordBtn = document.getElementById("voiceBtn");
  const micIcon = document.getElementById("micIcon");
  const statusMessage = document.getElementById("statusMessage");
  const chatWindow = document.getElementById("chatWindow");
  const personaSelect = document.getElementById("personaSelect");
  const textInput = document.getElementById("textInput");
  const sendBtn = document.getElementById("sendBtn");
  const saveApiKeysBtn = document.getElementById("saveApiKeys");

  // API input fields
  const murfApiInput = document.getElementById("murfApi");
  const assemblyApiInput = document.getElementById("assemblyApi");
  const geminiApiInput = document.getElementById("geminiApi");

  // State
  let isRecording = false;
  let ws = null;
  let audioContext;
  let mediaStream;
  let processor;
  let audioQueue = [];
  let isPlaying = false;

  // ---- Helper: Show status popup ----
  const showStatus = (msg) => {
    statusMessage.textContent = msg;
    statusMessage.style.display = "block";
    setTimeout(() => {
      statusMessage.style.display = "none";
    }, 3000);
  };

  // ---- Chat UI ----
  const addMessage = (text, type) => {
    const div = document.createElement("div");
    div.className = `message ${type === "user" ? "user-message" : "bot-message"}`;
    const timestamp = new Date().toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit"
    });
    div.innerHTML = `<div class="timestamp">${timestamp}</div><div>${text}</div>`;
    chatWindow.appendChild(div);
    chatWindow.scrollTop = chatWindow.scrollHeight;
  };

  // ---- Audio Playback ----
  const playNextInQueue = () => {
    if (!audioQueue.length) {
      isPlaying = false;
      return;
    }
    isPlaying = true;
    const base64Audio = audioQueue.shift();
    const audioData = Uint8Array.from(atob(base64Audio), (c) => c.charCodeAt(0)).buffer;

    audioContext.decodeAudioData(audioData)
      .then((buffer) => {
        const source = audioContext.createBufferSource();
        source.buffer = buffer;
        source.connect(audioContext.destination);
        source.onended = playNextInQueue;
        source.start();
      })
      .catch((e) => {
        console.error("Audio decode error:", e);
        playNextInQueue();
      });
  };

  // ---- API Keys: Load + Save ----
  const loadApiKeys = () => {
    murfApiInput.value = localStorage.getItem("murfApiKey") || "";
    assemblyApiInput.value = localStorage.getItem("assemblyApiKey") || "";
    geminiApiInput.value = localStorage.getItem("geminiApiKey") || "";
  };
  loadApiKeys();

  saveApiKeysBtn.addEventListener("click", () => {
    const murfKey = murfApiInput.value.trim();
    const assemblyKey = assemblyApiInput.value.trim();
    const geminiKey = geminiApiInput.value.trim();

    if (murfKey && assemblyKey && geminiKey) {
      localStorage.setItem("murfApiKey", murfKey);
      localStorage.setItem("assemblyApiKey", assemblyKey);
      localStorage.setItem("geminiApiKey", geminiKey);
      showStatus("✅ API Keys saved successfully!");
    } else {
      showStatus("⚠ Please enter all API keys.");
    }
  });

  // ---- Recording ----
  const startRecording = async () => {
    try {
      mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });

      await audioContext.audioWorklet.addModule("/static/recorder-worklet.js");
      const source = audioContext.createMediaStreamSource(mediaStream);

      processor = new AudioWorkletNode(audioContext, "recorder-worklet");
      processor.port.onmessage = (event) => {
        const inputData = event.data;
        const pcmData = new Int16Array(inputData.length);
        for (let i = 0; i < inputData.length; i++) {
          pcmData[i] = Math.max(-1, Math.min(1, inputData[i])) * 32767;
        }
        if (ws && ws.readyState === WebSocket.OPEN) {
          ws.send(pcmData.buffer);
        }
      };

      source.connect(processor);

      // ---- WebSocket setup ----
      let wsUrl;
      const protocol = location.protocol ==='https:'? 'wss:':'ws:';
      wsUrl = `${protocol}//${location.host}/ws`
      // if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") {
      //   wsUrl = "ws://127.0.0.1:8000/ws"; // Local
      // } else {
      //   wsUrl = "wss://echobot-api.onrender.com/ws"; // Render (deployed)
      // }
      ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        ws.send(JSON.stringify({
          type: "persona",
          persona: personaSelect.value,
          murfApiKey: localStorage.getItem("murfApiKey"),
          assemblyApiKey: localStorage.getItem("assemblyApiKey"),
          geminiApiKey: localStorage.getItem("geminiApiKey")
        }));
        showStatus("🎤 Connected, Listening...");
        micIcon.className = "fas fa-stop recording";
      };

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          switch (msg.type) {
            case "assistant":
              addMessage(msg.text, "bot");
              break;
            case "final":
              addMessage(msg.text, "user");
              break;
            case "audio":
              audioQueue.push(msg.b64);
              if (!isPlaying) playNextInQueue();
              break;
          }
        } catch (err) {
          console.error("Invalid WS message:", event.data, err);
        }
      };

      ws.onclose = () => {
        showStatus("🔌 Disconnected");
        micIcon.className = "fas fa-microphone";
      };

      ws.onerror = (err) => {
        console.error("WebSocket error:", err);
        showStatus("❌ WebSocket error");
      };

      isRecording = true;
      showStatus("🎙️ Recording...");
    } catch (err) {
      console.error("Recording failed:", err);
      showStatus("⚠ Mic access denied or unavailable.");
      alert("Microphone access is required to use EchoBot.");
    }
  };

  // ---- Stop Recording ----
  const stopRecording = () => {
    if (processor) processor.disconnect();
    if (mediaStream) mediaStream.getTracks().forEach((track) => track.stop());
    if (ws) {
      ws.close();
      ws = null;
    }

    isRecording = false;
    showStatus("✅ Ready");
    micIcon.className = "fas fa-microphone";
  };

  recordBtn.addEventListener("click", () => {
    if (isRecording) stopRecording();
    else startRecording();
  });

  // ---- Text Chat ----
  const sendMessage = () => {
    const text = textInput.value.trim();
    if (!text) return;
    addMessage(text, "user");
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "user_message", text }));
    }
    textInput.value = "";
  };

  sendBtn.addEventListener("click", sendMessage);
  textInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendMessage();
  });

  // ---- Persona ----
  personaSelect.addEventListener("change", () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "persona", persona: personaSelect.value }));
      showStatus(`Persona changed to "${personaSelect.value}"`);
    }
  });
});

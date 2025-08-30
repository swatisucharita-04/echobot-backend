// // server.js (Node.js, minimal)
// import express from "express";
// import { WebSocketServer } from "ws";
// import fetch from "node-fetch";
// import { MongoClient } from "mongodb";
// import fs from "fs";
// import path from "path";

// const app = express();
// app.use(express.json());

// const wss = new WebSocketServer({ noServer: true });
// const server = app.listen(3000);
// server.on("upgrade", (req, socket, head) => {
//   // Very minimal auth-checking here; add token checks in prod
//   wss.handleUpgrade(req, socket, head, (ws) => {
//     wss.emit("connection", ws, req);
//   });
// });

// // MongoDB setup (fill in your URI)
// const mongo = new MongoClient(process.env.MONGO_URI);
// await mongo.connect();
// const db = mongo.db("agent");
// const chats = db.collection("chats");

// // simple in-memory buffer per client
// const clients = new Map();

// wss.on("connection", (ws) => {
//   const id = Math.random().toString(36).slice(2);
//   clients.set(id, { ws, audioBuffers: [] });

//   ws.on("message", async (msg) => {
//     // messages can be JSON control or binary audio
//     if (typeof msg === "string") {
//       const data = JSON.parse(msg);
//       if (data.type === "end_of_utterance") {
//         // assemble audio, send to STT, then flow
//         const client = clients.get(id);
//         const audioBuffer = Buffer.concat(client.audioBuffers);
//         client.audioBuffers = [];
//         // Save audio to tmp file
//         const tmpPath = path.join("/tmp", `${id}.webm`);
//         fs.writeFileSync(tmpPath, audioBuffer);
//         // 1) Transcribe using your STT (OpenAI or Whisper or other)
//         const userText = await transcribeFile(tmpPath);
//         // 2) Call LLM with persona + history
//         const personaSystemPrompt = getPersonaSystemPrompt("pirate"); // example
//         const assistantText = await callLLM(personaSystemPrompt, userText, id);
//         // 3) Save to DB
//         await chats.insertOne({
//           clientId: id,
//           userText,
//           assistantText,
//           persona: "pirate",
//           createdAt: new Date(),
//         });
//         // 4) Generate audio via Murf (or another TTS)
//         const audioStream = await getMurfAudioStream(assistantText, "pirate-voice");
//         // 5) Stream audio binary back to client as chunks
//         for await (const chunk of audioStream) {
//           // send binary
//           ws.send(chunk);
//         }
//         // Optionally send final JSON with assistant text
//         ws.send(JSON.stringify({ type: "assistant_text", text: assistantText }));
//       } else if (data.type === "control") {
//         // handle other control messages
//       }
//     } else {
//       // binary piece of audio blob from client
//       const client = clients.get(id);
//       client.audioBuffers.push(msg); // accumulate Buffer
//     }
//   });

//   ws.on("close", () => clients.delete(id));
// });

// // STT function - implement using your chosen provider
// async function transcribeFile(filepath) {
//   // Example: call OpenAI Whisper transcription endpoint (pseudo)
//   // return string
//   // Or call another provider and return text
//   return "Transcribed user text (replace with real transcription)";
// }

// // LLM function - use your LLM API
// async function callLLM(systemPrompt, userText, clientId) {
//   // Retrieve recent history from DB to include as context
//   const recent = await chats.find({ clientId }).sort({ createdAt: -1 }).limit(6).toArray();
//   const messages = [
//     { role: "system", content: systemPrompt },
//     // include history in chronological order
//     ...recent.reverse().flatMap(r => ([
//       { role: "user", content: r.userText },
//       { role: "assistant", content: r.assistantText },
//     ])),
//     { role: "user", content: userText },
//   ];
//   // Call your LLM (OpenAI example)
//   const res = await fetch("https://api.openai.com/v1/chat/completions", {
//     method: "POST",
//     headers: {
//       Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
//       "Content-Type": "application/json",
//     },
//     body: JSON.stringify({
//       model: "gpt-4o-mini", // use your model
//       messages,
//       max_tokens: 600,
//     }),
//   });
//   const j = await res.json();
//   return j.choices?.?.message?.content ?? "Sorry, I couldn't think of a reply.";
// }

// // Murf TTS - pseudo implementation depending on Murf API
// async function getMurfAudioStream(text, voice) {
//   // Option A: Murf returns a final audio file URL => fetch it and create an async iterable over response.body
//   // Option B: Murf supports streaming => adapt accordingly
//   // Example pseudo:
//   const createRes = await fetch("https://api.murf.ai/v1/tts/create", {
//     method: "POST",
//     headers: {
//       Authorization: `Bearer ${process.env.MURF_API_KEY}`,
//       "Content-Type": "application/json",
//     },
//     body: JSON.stringify({ voice, text }),
//   });
//   const job = await createRes.json();
//   // Poll job or request audio URL
//   const audioUrl = job.audio_url;
//   const audioRes = await fetch(audioUrl);
//   // body is a Node ReadableStream; convert to async iterator of Uint8Array chunks
//   const reader = audioRes.body.getReader();
//   return {
//     async *[Symbol.asyncIterator]() {
//       while (true) {
//         const { done, value } = await reader.read();
//         if (done) break;
//         yield Buffer.from(value);
//       }
//     }
//   };
// }

// function getPersonaSystemPrompt(name) {
//   if (name === "pirate") {
//     return `You are "Captain Saltbeard", a friendly but salty pirate assistant. Speak with pirate flavor: use nautical metaphors, occasional "Arr!" but remain helpful, concise, and clear. Use one-liners, offer stepwise help when needed, and when giving instructions keep them safe and accurate. Do not roleplay illegal activity. Tone: adventurous, playful, slightly archaic.`;
//   }
//   return "You are a helpful assistant.";
// }
// const express = require("express");
// const axios = require("axios");
// const bodyParser = require("body-parser");
// const app = express();

// app.use(bodyParser.json());

// require('dotenv').config();


// // TTS endpoint: /api/tts?voice=matvela or ?voice=natella
// app.post("/api/tts", async (req, res) => {
//   const { text } = req.body;
//   const voice = req.query.voice || "Natalie"; // default Matvela

//   if (!text) return res.status(400).send("Missing text");

//   try {
//     const response = await axios.post(
//       "https://api.murf.ai/v1/speech/generate",
//       {
//         voiceId: voice,  // choose voice dynamically
//         text,
//         format: "mp3"
//       },
//       {
//         headers: {
//           "Authorization": `Bearer ${process.env.MURF_API_KEY}`,
//           "Content-Type": "application/json"
//         },
//         responseType: "arraybuffer"
//       }
//     );

//     const audioBuffer = Buffer.from(response.data, "binary");
//     res.set("Content-Type", "audio/mpeg");
//     res.send(audioBuffer);

//   } catch (err) {
//     console.error(err);
//     res.status(500).send("Murf TTS error");
//   }
// });

// app.listen(3000, () => console.log("Server running on port 3000"));

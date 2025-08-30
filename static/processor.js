// processor.js
class PCMProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.buffer = [];
    this.sampleRate = 16000;
    this.chunkSize = this.sampleRate * 0.05; // 50ms
  }

  process(inputs) {
    const input = inputs[0];
    if (!input || !input[0]) return true;

    const channelData = input[0];
    for (let i = 0; i < channelData.length; i++) {
      this.buffer.push(Math.max(-1, Math.min(1, channelData[i])));
    }

    if (this.buffer.length >= this.chunkSize) {
      const bufferToSend = new ArrayBuffer(this.buffer.length * 2);
      const view = new DataView(bufferToSend);

      for (let i = 0; i < this.buffer.length; i++) {
        const s = this.buffer[i];
        const intSample = s < 0 ? Math.round(s * 0x8000) : Math.round(s * 0x7fff);
        view.setInt16(i * 2, intSample, true);
      }

      try {
        this.port.postMessage(bufferToSend);
      } catch (e) {
        // ignore if port is closed
      }

      this.buffer = [];
    }

    return true;
  }
}

registerProcessor("recorder-processor", PCMProcessor);

class RecorderWorklet extends AudioWorkletProcessor {
  constructor() {
    super();
    this.buffer = [];
    this.targetSize = 16000 * 0.2; // 200ms of audio @ 16kHz
  }

  process(inputs) {
    const input = inputs[0];
    if (input && input[0]) {
      this.buffer.push(...input[0]);

      // Only flush when we have ~200ms
      if (this.buffer.length >= this.targetSize) {
        this.port.postMessage(this.buffer.slice(0, this.targetSize));
        this.buffer = this.buffer.slice(this.targetSize);
      }
    }
    return true;
  }
}

registerProcessor("recorder-worklet", RecorderWorklet);

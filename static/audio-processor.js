class AudioProcessor extends AudioWorkletProcessor {
  process(inputs, outputs, parameters) {
    const input = inputs[0];
    const output = outputs[0];

    // Your audio processing logic goes here
    // input and output are arrays of Float32Array channels
    for (let channel = 0; channel < output.length; ++channel) {
      output[channel].set(input[channel]); // Example: Pass through audio
    }

    return true; // Keep the processor alive
  }
}

registerProcessor('audio-processor', AudioProcessor);

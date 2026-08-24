with open("frontend/src/lib/speech.ts", "r") as f:
    text = f.read()

new_catch = """currentAudio.play().catch(e => {
    if (e.name === 'AbortError') {
      return; // Ignore aborts from rapid re-renders
    }
    console.error("Audio playback failed:", e);
    notifyStateChange(false);
  });"""

text = text.replace("""currentAudio.play().catch(e => {
    console.error("Audio playback failed:", e);
    notifyStateChange(false);
  });""", new_catch)

with open("frontend/src/lib/speech.ts", "w") as f:
    f.write(text)

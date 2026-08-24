import re

with open("frontend/src/app/chat/page.tsx", "r") as f:
    page = f.read()

# Update imports
page = page.replace("createSpeechRecognition, isSpeechRecognitionSupported", "startRecording, stopRecording")

# Replace startListening
old_start = """
  const startListening = () => {
    const recognition = createSpeechRecognition(language);
    if (!recognition) {
      alert('Voice input is not supported in your browser. Please use Chrome or Brave.');
      return;
    }
    recognitionRef.current = recognition;
    setIsListening(true);

    recognition.onresult = (event: any) => {
      const transcript = Array.from(event.results)
        .map((result: any) => result[0].transcript)
        .join('');
      setInput(transcript);
    };

    recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognition.start();
  };
"""

new_start = """
  const startListening = () => {
    setIsListening(true);
    startRecording(
      language,
      (text) => setInput(text),
      (err) => console.error(err),
      () => setIsListening(false)
    );
  };
"""

page = page.replace(old_start.strip(), new_start.strip())

old_stop = """
  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      recognitionRef.current = null;
    }
    setIsListening(false);
  };
"""

new_stop = """
  const stopListening = () => {
    stopRecording();
    setIsListening(false);
  };
"""

page = page.replace(old_stop.strip(), new_stop.strip())

with open("frontend/src/app/chat/page.tsx", "w") as f:
    f.write(page)

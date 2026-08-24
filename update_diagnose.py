import re

with open("frontend/src/app/diagnose/page.tsx", "r") as f:
    page = f.read()

# Update imports
page = page.replace("createSpeechRecognition, isSpeechRecognitionSupported", "startRecording, stopRecording")

# Replace startFollowUpListening
old_start = """
  const startFollowUpListening = () => {
    const recognition = createSpeechRecognition(language);
    if (!recognition) return;
    recognitionRef.current = recognition;
    setIsListening(true);
    recognition.onresult = (event: any) => {
      const transcript = Array.from(event.results).map((r: any) => r[0].transcript).join('');
      setFollowUpInput(transcript);
    };
    recognition.onerror = () => setIsListening(false);
    recognition.onend = () => setIsListening(false);
    recognition.start();
  };
"""

new_start = """
  const startFollowUpListening = () => {
    setIsListening(true);
    startRecording(
      language,
      (text) => setFollowUpInput(text),
      (err) => console.error(err),
      () => setIsListening(false)
    );
  };
"""

page = page.replace(old_start.strip(), new_start.strip())

old_stop = """
  const stopFollowUpListening = () => {
    if (recognitionRef.current) { recognitionRef.current.stop(); recognitionRef.current = null; }
    setIsListening(false);
  };
"""

new_stop = """
  const stopFollowUpListening = () => {
    stopRecording();
    setIsListening(false);
  };
"""

page = page.replace(old_stop.strip(), new_stop.strip())

with open("frontend/src/app/diagnose/page.tsx", "w") as f:
    f.write(page)

import re

def insert_stop_button(file_path):
    with open(file_path, "r") as f:
        page = f.read()

    # Import onSpeechStateChange
    page = page.replace('speakText, stopSpeaking, startRecording, stopRecording', 'speakText, stopSpeaking, startRecording, stopRecording, onSpeechStateChange')

    # Add state
    state_hook = """  const [isSpeakingActive, setIsSpeakingActive] = useState(false);
  useEffect(() => {
    return onSpeechStateChange(setIsSpeakingActive);
  }, []);
"""
    if "const [isListening" in page:
        page = page.replace("  const [isListening", state_hook + "\n  const [isListening", 1)
    
    # Add Stop Audio floating button
    floating_btn = """
      {/* Global Stop Audio Button */}
      {isSpeakingActive && (
        <div className="fixed bottom-24 left-1/2 -translate-x-1/2 z-50 animate-in fade-in slide-in-from-bottom-4">
          <button
            onClick={stopSpeaking}
            className="flex items-center gap-2 bg-red-600 text-white px-4 py-2 rounded-full shadow-lg hover:bg-red-700 transition-all font-medium"
          >
            <VolumeX className="h-4 w-4" />
            {t('Stop Audio', language) || 'Stop Audio'}
          </button>
        </div>
      )}
"""
    # Insert right before the final closing div tag
    # The last `</div>` in chat/page.tsx and diagnose/page.tsx
    # We can just insert it before `return (`... wait, inside the return.
    # Actually, we can replace `return (` with `return (\n    <>` and the very end with `{floating_btn}</>`
    
    # It's safer to just insert it right after the first <div ...> inside return
    match = re.search(r'return\s*\(\s*<div[^>]*>', page)
    if match:
        page = page[:match.end()] + floating_btn + page[match.end():]
    else:
        print(f"Failed to find return in {file_path}")

    with open(file_path, "w") as f:
        f.write(page)

insert_stop_button("frontend/src/app/chat/page.tsx")
insert_stop_button("frontend/src/app/diagnose/page.tsx")

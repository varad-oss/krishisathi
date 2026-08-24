import re

def update_file(filepath):
    with open(filepath, "r") as f:
        content = f.read()
    
    # Remove the global Stop Audio button
    content = re.sub(
        r'\{\s*/\*\s*Global Stop Audio Button\s*\*/\s*\}\s*\{isSpeakingActive && \(\s*<div className="fixed bottom-24.*?</div>\s*\)\}', 
        '', 
        content, 
        flags=re.DOTALL
    )
    
    # Replace Read Aloud button in chat/page.tsx (and diagnose/page.tsx follow-up)
    read_aloud_btn_regex = r'<button\s+onClick=\{\(\) => speakText\(msg\.content,\s*language\)\}\s+className="mt-1 flex items-center gap-1 text-xs text-gray-400 hover:text-green-600"\s*>\s*<Volume2 className="h-3 w-3" /> \{t\(\'Read Aloud\', language\)\}\s*</button>'
    
    new_btn = """<button
                  onClick={() => isSpeakingActive ? stopSpeaking() : speakText(msg.content, language)}
                  className={`mt-1 flex items-center gap-1 text-xs ${isSpeakingActive ? 'text-red-500 hover:text-red-600 font-medium' : 'text-gray-400 hover:text-green-600'}`}
                >
                  {isSpeakingActive ? <VolumeX className="h-3 w-3" /> : <Volume2 className="h-3 w-3" />}
                  {isSpeakingActive ? t('Stop Reading', language) : t('Read Aloud', language)}
                </button>"""
                
    content = re.sub(read_aloud_btn_regex, new_btn, content, flags=re.DOTALL)
    
    # In chat/page.tsx there's also another Read Aloud button variant:
    read_aloud_btn_2_regex = r'<button\s+onClick=\{\(\) => speakText\(msg\.content,\s*language\)\}\s+className="mt-2 flex items-center gap-1 text-xs text-gray-400 hover:text-green-600 transition-colors"\s+title=\{t\(\'Read Aloud\', language\)\}\s*>\s*<Volume2 className="h-3\.5 w-3\.5" />\s*\{t\(\'Read Aloud\', language\)\}\s*</button>'
    
    new_btn_2 = """<button
                  onClick={() => isSpeakingActive ? stopSpeaking() : speakText(msg.content, language)}
                  className={`mt-2 flex items-center gap-1 text-xs transition-colors ${isSpeakingActive ? 'text-red-500 hover:text-red-600 font-medium' : 'text-gray-400 hover:text-green-600'}`}
                  title={isSpeakingActive ? t('Stop Reading', language) : t('Read Aloud', language)}
                >
                  {isSpeakingActive ? <VolumeX className="h-3.5 w-3.5" /> : <Volume2 className="h-3.5 w-3.5" />}
                  {isSpeakingActive ? t('Stop Reading', language) : t('Read Aloud', language)}
                </button>"""
                
    content = re.sub(read_aloud_btn_2_regex, new_btn_2, content, flags=re.DOTALL)
    
    # In diagnose/page.tsx, there's also the main Read Aloud button for the diagnosis result
    main_read_aloud_regex = r'<button\s+onClick=\{\(\) => \{\s*const text = `\$\{result\.disease_name\}\. \$\{result\.severity\}\. \$\{result\.treatment_plan\.immediate_actions\.join\([^)]+\)\}`;.*?\}\}\s+className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors font-medium"\s*>\s*<Volume2 className="h-4 w-4" />\s*\{t\(\'Read Aloud\', language\)\}\s*</button>'
    
    new_main_btn = """<button
                  onClick={() => {
                    if (isSpeakingActive) {
                      stopSpeaking();
                    } else {
                      const text = `${result.disease_name}. ${result.severity}. ${result.treatment_plan.immediate_actions.join(', ')}`;
                      speakText(text, language);
                    }
                  }}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors font-medium ${isSpeakingActive ? 'bg-red-50 text-red-600 hover:bg-red-100 border border-red-200' : 'bg-gray-100 hover:bg-gray-200 text-gray-700'}`}
                >
                  {isSpeakingActive ? <VolumeX className="h-4 w-4" /> : <Volume2 className="h-4 w-4" />}
                  {isSpeakingActive ? t('Stop Reading', language) : t('Read Aloud', language)}
                </button>"""
                
    content = re.sub(main_read_aloud_regex, new_main_btn, content, flags=re.DOTALL)
    
    with open(filepath, "w") as f:
        f.write(content)

update_file("frontend/src/app/chat/page.tsx")
update_file("frontend/src/app/diagnose/page.tsx")

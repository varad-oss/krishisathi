with open("frontend/src/app/diagnose/page.tsx", "r") as f:
    page = f.read()

old_btn = """<button
                  onClick={() => {
                    const text = `${result.disease_name}. ${result.severity}. ${result.treatment_plan.immediate_actions.join(', ')}`;
                    speakText(text, language);
                  }}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-700 hover:bg-blue-100 font-semibold rounded-lg transition-colors"
                >
                  <Activity className="h-4 w-4" /> {/* Reusing Activity icon for audio/speaker since Volume/Speaker isn't imported */}
                  {t("Read Aloud", language)}
                </button>"""

new_btn = """<button
                  onClick={() => {
                    if (isSpeakingActive) {
                      stopSpeaking();
                    } else {
                      const text = `${result.disease_name}. ${result.severity}. ${result.treatment_plan.immediate_actions.join(', ')}`;
                      speakText(text, language);
                    }
                  }}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors font-semibold ${isSpeakingActive ? 'bg-red-50 text-red-600 hover:bg-red-100' : 'bg-blue-50 text-blue-700 hover:bg-blue-100'}`}
                >
                  {isSpeakingActive ? <VolumeX className="h-4 w-4" /> : <Volume2 className="h-4 w-4" />}
                  {isSpeakingActive ? t('Stop Reading', language) : t('Read Aloud', language)}
                </button>"""

page = page.replace(old_btn, new_btn)

with open("frontend/src/app/diagnose/page.tsx", "w") as f:
    f.write(page)

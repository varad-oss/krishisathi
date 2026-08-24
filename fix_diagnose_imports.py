import re

with open("frontend/src/app/diagnose/page.tsx", "r") as f:
    page = f.read()

page = page.replace("Volume2, AlertCircle } from 'lucide-react'", "Volume2, VolumeX, AlertCircle } from 'lucide-react'")
page = page.replace("speakText, startRecording, stopRecording } from '@/lib/speech'", "speakText, stopSpeaking, startRecording, stopRecording, onSpeechStateChange } from '@/lib/speech'")

with open("frontend/src/app/diagnose/page.tsx", "w") as f:
    f.write(page)

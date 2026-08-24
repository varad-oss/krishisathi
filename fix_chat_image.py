import re

with open("frontend/src/app/chat/page.tsx", "r") as f:
    page = f.read()

# 1. Update imports
page = page.replace("MapPin, Satellite, Mic, MicOff, Volume2, VolumeX", "MapPin, Satellite, Mic, MicOff, Volume2, VolumeX, Image as ImageIcon, X")

# 2. Add state and ref
state_insert = """  const [input, setInput] = useState('');
  const [imageAttachment, setImageAttachment] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
"""
page = page.replace("  const [input, setInput] = useState('');", state_insert)

# 3. Handle File selection
handle_file_change = """
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = (event) => {
      const base64String = event.target?.result as string;
      setImageAttachment(base64String);
    };
    reader.readAsDataURL(file);
  };
  
  const handleSend = async (text: string) => {
"""
page = page.replace("  const handleSend = async (text: string) => {", handle_file_change)

# 4. Modify Message type and handleSend
page = page.replace("content: string;", "content: string;\n  imageUrl?: string;")
page = page.replace(
    "const newMessage: Message = { id: Date.now().toString(), role: 'user', content: text, timestamp: new Date() };",
    "const newMessage: Message = { id: Date.now().toString(), role: 'user', content: text, timestamp: new Date(), imageUrl: imageAttachment || undefined };"
)

# 5. Clear attachment on send
page = page.replace(
    "setMessages(prev => [...prev, newMessage]);",
    "setMessages(prev => [...prev, newMessage]);\n    const currentImage = imageAttachment;\n    setImageAttachment(null);"
)

# 6. Pass image to API
page = page.replace(
    "const response = await getAdvisory(text, 18.5204, 73.8567, 'Maize', language);",
    "const response = await getAdvisory(text, 18.5204, 73.8567, 'Maize', language, currentImage ? currentImage.split(',')[1] : undefined);"
)

# 7. Render image in chat bubbles
bubble_render = """<div className={`rounded-2xl px-4 py-2 text-sm max-w-full ${msg.role === 'user' ? 'bg-green-600 text-white' : 'bg-gray-100 text-gray-800'}`}>
                        {msg.imageUrl && (
                          <div className="mb-2 rounded-lg overflow-hidden border border-white/20">
                            <img src={msg.imageUrl} alt="Uploaded attachment" className="max-w-full max-h-48 object-cover" />
                          </div>
                        )}"""
page = re.sub(
    r'<div className=\{`rounded-2xl px-4 py-2 text-sm max-w-full \$\{msg\.role === \'user\' \? \'bg-green-600 text-white\' : \'bg-gray-100 text-gray-800\'\}`\}>',
    bubble_render,
    page
)

# 8. Add UI for image attachment above input box
attachment_preview = """          {imageAttachment && (
            <div className="mb-2 relative inline-block">
              <img src={imageAttachment} alt="Attachment preview" className="h-16 w-16 object-cover rounded-lg border border-gray-200" />
              <button 
                onClick={() => setImageAttachment(null)}
                className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 shadow-sm hover:bg-red-600"
              >
                <X className="h-3 w-3" />
              </button>
            </div>
          )}
          <div className="relative flex items-center">
"""
page = page.replace('<div className="relative flex items-center">', attachment_preview)

# 9. Add hidden input and button in the input area
input_buttons = """
              <input 
                type="file" 
                ref={fileInputRef} 
                onChange={handleFileChange} 
                accept="image/*" 
                className="hidden" 
              />
              <button
                onClick={() => fileInputRef.current?.click()}
                className={`p-2 rounded-full transition-colors ${imageAttachment ? 'text-green-600 bg-green-50' : 'text-gray-400 hover:text-green-600 hover:bg-gray-100'}`}
                title="Attach Image"
              >
                <ImageIcon className="h-5 w-5" />
              </button>
              <button
                onClick={() => {
"""
page = page.replace("""<button
                onClick={() => {""", input_buttons, 1)

with open("frontend/src/app/chat/page.tsx", "w") as f:
    f.write(page)

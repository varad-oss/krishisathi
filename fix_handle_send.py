import re

with open("frontend/src/app/chat/page.tsx", "r") as f:
    page = f.read()

old_handle_send = """  const handleSend = async (text: string) => {

    if (!text.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await getAdvisory(text, activeLocation.lat, activeLocation.lng, language);"""

new_handle_send = """  const handleSend = async (text: string) => {

    if (!text.trim() && !imageAttachment) return;
    
    const currentImage = imageAttachment;
    setImageAttachment(null);

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: new Date(),
      imageUrl: currentImage || undefined
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const imgBase64 = currentImage ? currentImage.split(',')[1] : undefined;
      const response = await getAdvisory(text, activeLocation.lat, activeLocation.lng, activeLocation.crop, language, imgBase64);"""

page = page.replace(old_handle_send, new_handle_send)

with open("frontend/src/app/chat/page.tsx", "w") as f:
    f.write(page)

import re

with open("frontend/src/app/chat/page.tsx", "r") as f:
    page = f.read()

# 1. Bubble rendering
bubble_start = """              <div className={cn(
                "rounded-2xl px-5 py-3 shadow-sm",
                msg.role === 'user' 
                  ? "bg-green-700 text-white rounded-tr-sm" 
                  : "bg-gray-100 text-gray-800 rounded-tl-sm border border-gray-200"
              )}>"""

bubble_insert = """              <div className={cn(
                "rounded-2xl px-5 py-3 shadow-sm",
                msg.role === 'user' 
                  ? "bg-green-700 text-white rounded-tr-sm" 
                  : "bg-gray-100 text-gray-800 rounded-tl-sm border border-gray-200"
              )}>
                {msg.imageUrl && (
                  <div className="mb-3 rounded-lg overflow-hidden border border-white/20">
                    <img src={msg.imageUrl} alt="Uploaded attachment" className="max-w-full max-h-48 object-cover rounded-md" />
                  </div>
                )}"""

page = page.replace(bubble_start, bubble_insert)

# 2. Input area - preview and upload button
input_area_old = """          <form 
            onSubmit={(e) => { e.preventDefault(); handleSend(input); }}
            className="flex items-end gap-2"
          >
            <textarea"""

input_area_new = """          <form 
            onSubmit={(e) => { e.preventDefault(); handleSend(input); }}
            className="flex flex-col gap-2"
          >
            {imageAttachment && (
              <div className="relative inline-block self-start">
                <img src={imageAttachment} alt="Attachment preview" className="h-20 object-cover rounded-lg border border-gray-300 shadow-sm" />
                <button 
                  type="button"
                  onClick={() => setImageAttachment(null)}
                  className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 shadow-sm hover:bg-red-600 z-10"
                >
                  <X className="h-3 w-3" />
                </button>
              </div>
            )}
            <div className="flex items-end gap-2">
            <input 
              type="file" 
              ref={fileInputRef} 
              onChange={handleFileChange} 
              accept="image/*" 
              className="hidden" 
            />
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className={`p-3 rounded-full transition-colors flex items-center justify-center ${imageAttachment ? 'text-green-600 bg-green-50' : 'text-gray-500 hover:text-green-600 hover:bg-green-50 bg-gray-50 border border-gray-200'}`}
              title="Attach Image"
            >
              <ImageIcon className="h-5 w-5" />
            </button>
            <textarea"""

page = page.replace(input_area_old, input_area_new)

# Since I wrapped the textarea and buttons in a div, I need to close the div before the form closes!
form_end_old = """              </button>
            </button>
          </form>"""
# Wait, let's see how the form ends exactly.

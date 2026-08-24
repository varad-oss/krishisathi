import re

with open("frontend/src/app/chat/page.tsx", "r") as f:
    page = f.read()

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

with open("frontend/src/app/chat/page.tsx", "w") as f:
    f.write(page)

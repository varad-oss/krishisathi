import re

with open("frontend/src/app/chat/page.tsx", "r") as f:
    page = f.read()

# Fix the dangling div
page = page.replace("            </button>\n            </div>\n          </form>", "            </button>\n          </form>")

# Re-apply the form UI
old_form = """          <form 
            onSubmit={(e) => { e.preventDefault(); handleSend(input); }}
            className="flex items-end gap-2"
          >
            <textarea"""

new_form = """          <form 
            onSubmit={(e) => { e.preventDefault(); handleSend(input); }}
            className="flex flex-col gap-2"
          >
            {imageAttachment && (
              <div className="relative inline-block self-start mb-2">
                <img src={imageAttachment} alt="Attachment preview" className="h-16 w-16 object-cover rounded-lg border border-gray-300 shadow-sm" />
                <button 
                  type="button"
                  onClick={() => setImageAttachment(null)}
                  className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 shadow-sm hover:bg-red-600 z-10"
                >
                  <X className="h-3 w-3" />
                </button>
              </div>
            )}
            <div className="flex items-end gap-2 w-full">
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
              className={`h-[44px] w-[44px] flex-shrink-0 flex items-center justify-center rounded-xl transition-colors ${imageAttachment ? 'text-green-600 bg-green-100 hover:bg-green-200' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
              title="Attach Image"
            >
              <ImageIcon className="h-5 w-5" />
            </button>
            <textarea"""

page = page.replace(old_form, new_form)

# Add the closing div for the flex container inside form
old_form_close = """              <Send className="h-5 w-5" />
            </button>
          </form>"""

new_form_close = """              <Send className="h-5 w-5" />
            </button>
            </div>
          </form>"""

page = page.replace(old_form_close, new_form_close)

with open("frontend/src/app/chat/page.tsx", "w") as f:
    f.write(page)

import Link from 'next/link';

export default function Footer() {
  return (
    <footer className="bg-gray-50 border-t">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center justify-between gap-4 sm:flex-row">
          <div className="flex flex-col items-center sm:items-start">
            <span className="text-xl font-bold text-green-900 flex items-center gap-2">
              🌾 KrishiSathi
            </span>
            <p className="mt-2 text-sm text-gray-500">
              Built for Build with AI: Code for Communities
            </p>
          </div>
          
          <div className="flex flex-col items-center sm:items-end gap-2">
            <div className="flex gap-4">
              <Link href="#" className="text-sm text-gray-600 hover:text-green-700">
                GitHub
              </Link>
              <Link href="#" className="text-sm text-gray-600 hover:text-green-700">
                AgriN Initiative
              </Link>
              <Link href="#" className="text-sm text-gray-600 hover:text-green-700">
                Privacy
              </Link>
            </div>
            <div className="mt-2 flex items-center gap-2 rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700 border border-blue-100">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
              </span>
              Powered by Google AI
            </div>
          </div>
        </div>
        <div className="mt-8 border-t border-gray-200 pt-8 text-center text-sm text-gray-500">
          &copy; {new Date().getFullYear()} KrishiSathi. All rights reserved.
        </div>
      </div>
    </footer>
  );
}

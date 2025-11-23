'use client'

import { useState } from 'react'
import Link from 'next/link'

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <nav className="bg-white border-b mb-4 sticky top-0 z-50">
      <div className="container mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          <Link href="/" className="font-bold text-xl whitespace-nowrap">
            🏥 Assistente Hospitalar
          </Link>
          
          {/* Menu Desktop */}
          <div className="hidden md:flex gap-2">
            <Link href="/about" className="px-3 py-1 hover:bg-gray-100 rounded text-sm">
              Sobre
            </Link>
            <Link href="/chat" className="px-3 py-1 hover:bg-gray-100 rounded text-sm">
              💬 Chat
            </Link>
            <Link href="/sql-workbench" className="px-3 py-1 hover:bg-gray-100 rounded text-sm">
              🔧 SQL
            </Link>
            <Link href="/compliance" className="px-3 py-1 hover:bg-gray-100 rounded text-sm">
              📋 Compliance
            </Link>
            <Link href="/observability" className="px-3 py-1 hover:bg-gray-100 rounded text-sm">
              📊 Observability
            </Link>
          </div>

          {/* Botão Hambúrguer Mobile */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="md:hidden p-2 rounded-lg hover:bg-gray-100"
            aria-label="Toggle menu"
          >
            <svg
              className="w-6 h-6"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              {isOpen ? (
                <path d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>

        {/* Menu Mobile */}
        {isOpen && (
          <div className="md:hidden mt-4 pb-2 border-t pt-2">
            <div className="flex flex-col gap-1">
              <Link
                href="/about"
                onClick={() => setIsOpen(false)}
                className="px-3 py-2 hover:bg-gray-100 rounded text-sm"
              >
                Sobre
              </Link>
              <Link
                href="/chat"
                onClick={() => setIsOpen(false)}
                className="px-3 py-2 hover:bg-gray-100 rounded text-sm"
              >
                💬 Chat
              </Link>
              <Link
                href="/sql-workbench"
                onClick={() => setIsOpen(false)}
                className="px-3 py-2 hover:bg-gray-100 rounded text-sm"
              >
                🔧 SQL
              </Link>
              <Link
                href="/compliance"
                onClick={() => setIsOpen(false)}
                className="px-3 py-2 hover:bg-gray-100 rounded text-sm"
              >
                📋 Compliance
              </Link>
              <Link
                href="/observability"
                onClick={() => setIsOpen(false)}
                className="px-3 py-2 hover:bg-gray-100 rounded text-sm"
              >
                📊 Observability
              </Link>
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}


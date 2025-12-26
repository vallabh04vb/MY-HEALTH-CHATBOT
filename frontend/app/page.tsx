'use client';

import { useState } from 'react';
import ChatInterface from '@/components/ChatInterface';

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                UHC Insurance Policy Assistant
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                AI-powered chatbot to help understand UnitedHealthcare policies
              </p>
            </div>
            <div className="flex items-center space-x-2 bg-blue-100 px-4 py-2 rounded-lg">
              <svg
                className="w-5 h-5 text-blue-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <span className="text-sm font-medium text-blue-900">
                Powered by llmops_lite
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <InfoCard
            title="Ask Questions"
            description="Query UHC policies in natural language"
            icon={
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            }
          />
          <InfoCard
            title="Get Sources"
            description="Every answer includes policy citations"
            icon={
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            }
          />
          <InfoCard
            title="Avoid Denials"
            description="Understand coverage criteria to prevent claims rejections"
            icon={
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            }
          />
        </div>

        {/* Chat Interface */}
        <ChatInterface />

        {/* Example Questions */}
        <div className="mt-6 bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">
            Example Questions
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <ExampleQuestion text="Is bariatric surgery covered for BMI 35?" />
            <ExampleQuestion text="What are criteria for knee replacement approval?" />
            <ExampleQuestion text="Does UHC cover genetic testing for breast cancer?" />
            <ExampleQuestion text="Prior authorization requirements for MRI scans?" />
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-500">
            Built with FastAPI, ChromaDB, llmops_lite, and Next.js
          </p>
          <p className="text-center text-xs text-gray-400 mt-2">
            Note: This chatbot provides information based on UHC policies.
            Always verify critical information with UHC directly.
          </p>
        </div>
      </footer>
    </main>
  );
}

function InfoCard({ title, description, icon }: { title: string; description: string; icon: React.ReactNode }) {
  return (
    <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0 text-blue-600">
          {icon}
        </div>
        <div>
          <h3 className="text-sm font-semibold text-gray-900">{title}</h3>
          <p className="text-sm text-gray-600 mt-1">{description}</p>
        </div>
      </div>
    </div>
  );
}

function ExampleQuestion({ text }: { text: string }) {
  return (
    <div className="text-sm text-gray-600 bg-gray-50 rounded-md px-3 py-2 border border-gray-200 hover:bg-gray-100 cursor-pointer transition-colors">
      "{text}"
    </div>
  );
}

'use client';

interface PolicySource {
  policy_id: string;
  title: string;
  url: string;
  excerpt?: string;
}

interface SourceCitationProps {
  sources: PolicySource[];
}

export default function SourceCitation({ sources }: SourceCitationProps) {
  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-4 pt-4 border-t border-gray-200">
      <div className="flex items-start space-x-2 mb-2">
        <svg
          className="w-4 h-4 text-gray-500 mt-0.5 flex-shrink-0"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <p className="text-xs font-semibold text-gray-700">
          Sources ({sources.length}):
        </p>
      </div>

      <div className="space-y-2">
        {sources.map((source, index) => (
          <SourceCard key={index} source={source} index={index + 1} />
        ))}
      </div>
    </div>
  );
}

function SourceCard({ source, index }: { source: PolicySource; index: number }) {
  return (
    <div className="bg-gray-50 rounded-md p-3 border border-gray-200 hover:border-blue-300 transition-colors">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-2">
            <span className="inline-flex items-center justify-center w-5 h-5 rounded-full bg-blue-100 text-blue-700 text-xs font-semibold">
              {index}
            </span>
            <h4 className="text-sm font-medium text-gray-900 line-clamp-1">
              {source.title}
            </h4>
          </div>

          <p className="text-xs text-gray-500 mt-1">
            Policy ID: {source.policy_id}
          </p>

          {source.excerpt && (
            <p className="text-xs text-gray-600 mt-2 line-clamp-2">
              "{source.excerpt}"
            </p>
          )}
        </div>

        {source.url && (
          <a
            href={source.url}
            target="_blank"
            rel="noopener noreferrer"
            className="ml-3 inline-flex items-center px-3 py-1 text-xs font-medium text-blue-700 bg-blue-50 rounded-md hover:bg-blue-100 transition-colors"
          >
            View
            <svg
              className="w-3 h-3 ml-1"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
              />
            </svg>
          </a>
        )}
      </div>
    </div>
  );
}

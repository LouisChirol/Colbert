'use client';

import ReactMarkdown from 'react-markdown';
import Image from 'next/image';

interface Source {
  url: string;
  title: string;
  excerpt: string;
}

interface MessageProps {
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
  isError?: boolean;
}

const Message = ({ role, content, sources = [], isError = false }: MessageProps) => {
  const isUser = role === 'user';

  const getAvatarSrc = () => {
    if (isError || content.includes("Désolé, une erreur est survenue. Veuillez réessayer.")) {
      return '/colbert_sorry.png';
    }
    return '/colbert_avatar.png';
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} gap-3`}>
      {!isUser && (
        <div className="w-12 h-12 rounded-full overflow-hidden flex-shrink-0">
          <Image
            src={getAvatarSrc()}
            alt="Colbert Assistant"
            width={48}
            height={48}
            className="w-full h-full object-cover"
          />
        </div>
      )}
      <div
        className={`max-w-[80%] rounded-lg p-4 ${
          isUser
            ? 'bg-blue-500 text-white'
            : isError || content.includes("Désolé, une erreur est survenue. Veuillez réessayer.")
            ? 'bg-red-100 text-red-800'
            : 'bg-gray-100 text-gray-800'
        }`}
      >
        <ReactMarkdown>{content}</ReactMarkdown>
        {sources.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <h4 className="text-sm font-semibold mb-2">Sources :</h4>
            <ul className="space-y-2">
              {sources.map((source, index) => (
                <li key={index} className="text-sm">
                  <a
                    href={source.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-500 hover:underline"
                  >
                    {source.title}
                  </a>
                  <p className="text-gray-600 mt-1">{source.excerpt}</p>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default Message; 
'use client';

import { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    skill_used?: string;
    created_at: string;
}

interface Conversation {
    id: string;
    title: string;
    created_at: string;
    updated_at: string;
    message_count: number;
}

export default function ChatPage() {
    const [conversations, setConversations] = useState<Conversation[]>([]);
    const [activeConversation, setActiveConversation] = useState<string | null>(null);
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        fetchConversations();
    }, []);

    useEffect(() => {
        if (activeConversation) {
            fetchMessages(activeConversation);
        }
    }, [activeConversation]);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const fetchConversations = async () => {
        try {
            const response = await fetch('http://localhost:8001/api/chat/conversations');
            const data = await response.json();
            setConversations(data);
        } catch (error) {
            console.error('Failed to fetch conversations:', error);
        }
    };

    const fetchMessages = async (conversationId: string) => {
        try {
            const response = await fetch(
                `http://localhost:8001/api/chat/conversations/${conversationId}`
            );
            const data = await response.json();
            setMessages(data.messages);
        } catch (error) {
            console.error('Failed to fetch messages:', error);
        }
    };

    const sendMessage = async () => {
        if (!input.trim()) return;

        const userMessage = input;
        setInput('');
        setLoading(true);

        try {
            const response = await fetch('http://localhost:8001/api/chat/message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    conversation_id: activeConversation,
                    message: userMessage
                })
            });

            const data = await response.json();

            // If new conversation, set it as active
            if (!activeConversation) {
                setActiveConversation(data.conversation_id);
                fetchConversations();
            } else {
                // Refresh messages
                fetchMessages(data.conversation_id);
            }
        } catch (error) {
            console.error('Failed to send message:', error);
        } finally {
            setLoading(false);
        }
    };

    const createNewConversation = () => {
        setActiveConversation(null);
        setMessages([]);
        setInput('');
    };

    const deleteConversation = async (id: string) => {
        try {
            await fetch(`http://localhost:8001/api/chat/conversations/${id}`, {
                method: 'DELETE'
            });
            fetchConversations();
            if (activeConversation === id) {
                createNewConversation();
            }
        } catch (error) {
            console.error('Failed to delete conversation:', error);
        }
    };

    return (
        <div className="flex h-screen bg-gray-50">
            {/* Sidebar */}
            {sidebarOpen && (
                <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
                    <div className="p-4 border-b border-gray-200">
                        <button
                            onClick={createNewConversation}
                            className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                        >
                            + New Chat
                        </button>
                    </div>

                    <div className="flex-1 overflow-y-auto">
                        {conversations.map((conv) => (
                            <div
                                key={conv.id}
                                className={`p-4 border-b border-gray-100 cursor-pointer hover:bg-gray-50 ${activeConversation === conv.id ? 'bg-blue-50' : ''
                                    }`}
                                onClick={() => setActiveConversation(conv.id)}
                            >
                                <div className="flex justify-between items-start">
                                    <div className="flex-1 min-w-0">
                                        <p className="text-sm font-medium text-gray-900 truncate">
                                            {conv.title}
                                        </p>
                                        <p className="text-xs text-gray-500 mt-1">
                                            {conv.message_count} messages
                                        </p>
                                    </div>
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            deleteConversation(conv.id);
                                        }}
                                        className="ml-2 text-gray-400 hover:text-red-600"
                                    >
                                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                        </svg>
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Main Chat Area */}
            <div className="flex-1 flex flex-col">
                {/* Header */}
                <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                        <button
                            onClick={() => setSidebarOpen(!sidebarOpen)}
                            className="text-gray-600 hover:text-gray-900"
                        >
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                            </svg>
                        </button>
                        <h1 className="text-xl font-semibold text-gray-900">
                            Research Assistant
                        </h1>
                        <span className="px-2 py-1 text-xs bg-yellow-100 text-yellow-800 rounded">
                            Mock Mode
                        </span>
                    </div>
                </div>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-6 space-y-4">
                    {messages.length === 0 && !activeConversation && (
                        <div className="text-center py-12">
                            <div className="inline-block p-4 bg-blue-100 rounded-full mb-4">
                                <svg className="w-12 h-12 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                                </svg>
                            </div>
                            <h2 className="text-2xl font-semibold text-gray-900 mb-2">
                                Welcome to Lymeric Research Assistant
                            </h2>
                            <p className="text-gray-600 mb-6">
                                Ask me about materials properties, synthesis, literature, or data analysis
                            </p>
                            <div className="max-w-2xl mx-auto grid grid-cols-2 gap-3">
                                <button
                                    onClick={() => setInput("What is the glass transition temperature of polystyrene?")}
                                    className="p-3 text-left bg-white rounded-lg border border-gray-200 hover:border-blue-300 hover:shadow"
                                >
                                    <p className="text-sm font-medium text-gray-900">Property Query</p>
                                    <p className="text-xs text-gray-500 mt-1">Ask about material properties</p>
                                </button>
                                <button
                                    onClick={() => setInput("Analyze the materials in the database")}
                                    className="p-3 text-left bg-white rounded-lg border border-gray-200 hover:border-blue-300 hover:shadow"
                                >
                                    <p className="text-sm font-medium text-gray-900">Data Analysis</p>
                                    <p className="text-xs text-gray-500 mt-1">Explore dataset statistics</p>
                                </button>
                                <button
                                    onClick={() => setInput("Find research papers on polymer synthesis")}
                                    className="p-3 text-left bg-white rounded-lg border border-gray-200 hover:border-blue-300 hover:shadow"
                                >
                                    <p className="text-sm font-medium text-gray-900">Literature Search</p>
                                    <p className="text-xs text-gray-500 mt-1">Search for relevant papers</p>
                                </button>
                                <button
                                    onClick={() => setInput("How do I synthesize polyethylene?")}
                                    className="p-3 text-left bg-white rounded-lg border border-gray-200 hover:border-blue-300 hover:shadow"
                                >
                                    <p className="text-sm font-medium text-gray-900">Synthesis Help</p>
                                    <p className="text-xs text-gray-500 mt-1">Get synthesis guidance</p>
                                </button>
                            </div>
                        </div>
                    )}

                    {messages.map((message) => (
                        <div
                            key={message.id}
                            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                            <div
                                className={`max-w-3xl rounded-lg p-4 ${message.role === 'user'
                                        ? 'bg-blue-600 text-white'
                                        : 'bg-white border border-gray-200'
                                    }`}
                            >
                                <div className="prose prose-sm max-w-none">
                                    {message.role === 'assistant' ? (
                                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                            {message.content}
                                        </ReactMarkdown>
                                    ) : (
                                        <p>{message.content}</p>
                                    )}
                                </div>
                                {message.skill_used && (
                                    <div className="mt-2 text-xs text-gray-500">
                                        <span className="px-2 py-1 bg-gray-100 rounded">
                                            {message.skill_used}
                                        </span>
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}

                    {loading && (
                        <div className="flex justify-start">
                            <div className="bg-white border border-gray-200 rounded-lg p-4">
                                <div className="flex space-x-2">
                                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                                </div>
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>

                {/* Input */}
                <div className="bg-white border-t border-gray-200 p-4">
                    <div className="max-w-4xl mx-auto flex space-x-4">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && !loading && sendMessage()}
                            placeholder="Ask me anything about materials research..."
                            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                            disabled={loading}
                        />
                        <button
                            onClick={sendMessage}
                            disabled={loading || !input.trim()}
                            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
                        >
                            Send
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

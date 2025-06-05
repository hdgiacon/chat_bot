"use client";

import { useState, useEffect, useRef } from "react";
import { FiSend } from "react-icons/fi";
import MainContainer from "@/components/main-container";
import Sidebar from "@/components/chat-sidebar";
import { TypingEffect } from "@/components/typing-effect";
import { getMessages, Message, getAnswer, createMessage, Reference } from "@/services/model";
import '../../styles/globals.css';


type FrontendTempMessage =
    | (Message & { temporary?: false })
    | {
        id: string;
        chat_id: number;
        text: string;
        is_user: boolean;
        created_at: string;
        temporary: true;
    };


export default function ChatPage() {
    const [selectedChatId, setSelectedChatId] = useState<number | null>(null);
    const [messages, setMessages] = useState<FrontendTempMessage[] | null>(null);
    const [loadingMessages, setLoadingMessages] = useState(false);
    const [prompt, setPrompt] = useState("");
    const [typingBotMessageIndex, setTypingBotMessageIndex] = useState<number | null>(null);
    const [isModalReferencesOpen, setIsModalReferencesOpen] = useState(false);
    const [modalReferences, setModalReferences] = useState<Reference[]>([]);

    const messagesEndRef = useRef<HTMLDivElement>(null);
    const bottomRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const fetchMessages = async () => {
            if (selectedChatId !== null) {
                setLoadingMessages(true);
                try {
                    const msgs = await getMessages(selectedChatId);
                    setMessages(msgs);
                } catch (err) {
                    setMessages([]);
                } finally {
                    setLoadingMessages(false);
                }
            } else {
                console.log("⚠️ selectedChatId NÃO é um número:", selectedChatId);
                setMessages(null);
            }
        };

        fetchMessages();
    }, [selectedChatId]);

    useEffect(() => {
        if (messagesEndRef.current) {
            messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
        }
    }, [messages]);

    useEffect(() => {
        if (bottomRef.current) {
            bottomRef.current.scrollIntoView({ behavior: "smooth" });
        }
    }, [messages]);

    const handleSendSentence = async () => {
        if (!selectedChatId || !prompt.trim()) return;

        const prompt_value = prompt;
        setPrompt("");

        await createMessage(selectedChatId, prompt_value, true);

        const msgs_with_user = await getMessages(selectedChatId);
        setMessages(msgs_with_user);

        const thinkingMessage: FrontendTempMessage = {
            id: "temp-thinking",
            chat_id: selectedChatId,
            text: "Thinking...",
            is_user: false,
            created_at: new Date().toISOString(),
            temporary: true,
        };

        setMessages([...msgs_with_user, thinkingMessage]);

        const answer = await getAnswer(prompt_value);

        await createMessage(selectedChatId, answer, false);

        const msgs_after_answer = await getMessages(selectedChatId);
        setMessages(msgs_after_answer);


        const lastBotMessageIndexCurrentAnswering = msgs_after_answer
            .map((msg, idx) => ({ msg, idx }))
            .filter(({ msg }) =>
                !msg.is_user &&
                (!('temporary' in msg) || !msg.temporary)
            )
            .map(({ idx }) => idx)
            .pop();

        if (lastBotMessageIndexCurrentAnswering !== undefined && lastBotMessageIndexCurrentAnswering !== -1) {
            setTypingBotMessageIndex(lastBotMessageIndexCurrentAnswering);
        }
    };

    const handleReferencesModal = (references: Reference[]) => {
        setModalReferences(references);
        setIsModalReferencesOpen(true);
    };

    return (
        <div className="flex h-screen">
            <Sidebar
                onSelectChat={(id: number) => setSelectedChatId(id)}
                selectedChatId={selectedChatId}
            />
            <MainContainer>
                {selectedChatId ? (
                    loadingMessages ? (
                        <main className="min-h-screen flex flex-col items-center justify-center gap-y-4">
                            <p className="text-[#FAFAFA] text-2xl">Loading messages...</p>
                        </main>
                    ) : messages && messages.length > 0 ? (
                        <div className="flex flex-col h-[90vh] w-full px-1 py-2">

                            <div className="flex-grow overflow-y-auto px-4 py-6 scrollbar">
                                <div className="space-y-4 max-w-4xl mx-auto">
                                    {messages.map((msg, index) => {
                                        let content = null;
                                        let references = [];

                                        try {
                                            const parsed = typeof msg.text === "string" ? JSON.parse(msg.text) : msg.text;
                                            if (parsed && typeof parsed === "object" && parsed.response) {
                                                content = parsed.response;
                                                references = parsed.references;
                                            } else {
                                                content = msg.text;
                                            }
                                        } catch {
                                            content = msg.text;
                                        }

                                        if (msg.is_user) {
                                            return (
                                                <div key={index} className="flex justify-end">
                                                    <div className="max-w-[70%] bg-[#313131] text-[#FAFAFA] p-3 rounded-2xl shadow whitespace-pre-wrap">
                                                        {content}
                                                    </div>
                                                </div>
                                            );
                                        }

                                        return (
                                            <div key={index} className="flex justify-start">
                                                <div className="max-w-[70%] bg-[#242424] text-[#FAFAFA] p-3 rounded-2xl whitespace-pre-wrap">
                                                    {msg.temporary ? (
                                                        <span className="thinking-dots">Thinking</span>
                                                    ) : (
                                                        <>
                                                            {typingBotMessageIndex === index ? (
                                                                <TypingEffect
                                                                    text={content}
                                                                    onFinish={() => setTypingBotMessageIndex(null)}
                                                                />
                                                            ) : (
                                                                <>
                                                                    {content}
                                                                    {references.length > 0 && (
                                                                        <>
                                                                            {" <\\"}
                                                                            <a
                                                                                href="#"
                                                                                onClick={(e) => {
                                                                                    e.preventDefault();
                                                                                    handleReferencesModal(references);
                                                                                }}
                                                                                className="text-purple-700 hover:underline"
                                                                            >
                                                                                See references
                                                                            </a>
                                                                            {">"}
                                                                        </>
                                                                    )}
                                                                </>
                                                            )}
                                                        </>
                                                    )}
                                                </div>
                                            </div>
                                        );
                                    })}
                                    <div ref={messagesEndRef} />
                                </div>
                            </div>

                            <div className="px-4 pt-2 pb-4">
                                <div className="flex items-center justify-center w-full gap-5">
                                    <input
                                        type="text"
                                        className="flex-grow max-w-3xl px-4 py-2 w-full border border-transparent rounded-md bg-[#313131] bg-opacity-10 focus:outline-none focus:ring-1 focus:ring-purple-500"
                                        placeholder="Ask something"
                                        value={prompt}
                                        onChange={(e) => setPrompt(e.target.value)}
                                        onKeyDown={(e) => {
                                            if (e.key === "Enter") {
                                                handleSendSentence();
                                            }
                                        }}
                                    />

                                    <button
                                        type="button"
                                        className="w-10 h-10 bg-purple-700 hover:bg-purple-800 text-[#FAFAFA] rounded-full flex items-center justify-center transition-colors"
                                        onClick={handleSendSentence}
                                    >
                                        <FiSend size={20} className="rotate-45" />
                                    </button>
                                </div>

                                <div className="flex justify-center mt-2">
                                    <p className="text-[#FAFAFA99] text-base text-center">
                                        This project uses as a database{" "}
                                        <a
                                            href="https://huggingface.co/datasets/habedi/stack-exchange-dataset"
                                            onClick={(e) => console.log("nada ainda")}
                                            className="text-purple-700 hover:underline"
                                        >
                                            habedi/stack-exchange-dataset
                                        </a>
                                        .
                                    </p>
                                </div>
                            </div>
                        </div>
                    ) : (

                        <main className="min-h-screen flex flex-col items-center justify-center gap-y-5">
                            <div className="flex flex-row items-center gap-x-5">
                                <h1 className="text-[#FAFAFA] text-5xl font-semibold">How can I help?</h1>
                                <img
                                    src="/chatbot_logo.png"
                                    width={180}
                                    height={180}
                                    alt="Logo do Chatbot"
                                />
                            </div>

                            <div className="flex items-center justify-center w-full mx-auto gap-5">
                                <input
                                    type="text"
                                    className="flex-grow max-w-3xl px-4 py-2 w-full border border-transparent rounded-md bg-[#313131] bg-opacity-10 focus:outline-none focus:ring-1 focus:ring-purple-500"
                                    placeholder="Ask something"
                                    onChange={(e) => setPrompt(e.target.value)}
                                    value={prompt}
                                    onKeyDown={(e) => {
                                        if (e.key === 'Enter') {
                                            handleSendSentence()
                                        }
                                    }}
                                />

                                <button
                                    type="button"
                                    className="w-10 h-10 bg-purple-700 hover:bg-purple-800 text-[#FAFAFA] rounded-full flex items-center justify-center transition-colors"
                                    onClick={handleSendSentence}
                                >
                                    <FiSend size={20} className="rotate-45" />
                                </button>
                            </div>

                            <p className="text-[#FAFAFA99]">
                                This project uses as a database{' '}
                                <a href="https://huggingface.co/datasets/habedi/stack-exchange-dataset" onClick={(e) => console.log('nada ainda')} className="text-purple-700 hover:underline">
                                    habedi/stack-exchange-dataset
                                </a>
                                .
                            </p>
                        </main>
                    )

                ) : (

                    <main className="min-h-screen flex flex-col items-center justify-center gap-y-15">
                        <div className="flex flex-row items-center gap-x-5">
                            <h1 className="text-[#FAFAFA] text-6xl font-semibold">ChatBot</h1>
                            <img
                                src="/chatbot_logo.png"
                                width={200}
                                height={200}
                                alt="Logo do Chatbot"
                            />
                        </div>

                        <p className="text-[#FAFAFA] text-4xl text-center max-w-5xl">
                            The database of this project has information from the areas of&nbsp;
                            <span className="text-purple-700">Computer Science</span>
                            &nbsp;and&nbsp;
                            <span className="text-purple-700">Data Science</span>.
                        </p>

                        <p className="text-[#FAFAFA] text-4xl text-center max-w-xl">
                            Start by creating a <span className="text-purple-700">New Chat</span>.
                        </p>

                        <p className="text-[#FAFAFA] text-2xl text-center max-w-xl">
                            See also:
                        </p>

                        <div className="flex flex-row items-center gap-x-5">
                            <a
                                href="https://arxiv.org/pdf/1706.03762"
                                target="_blank"
                                rel="transformers_article"
                                className="max-w-sm p-6 bg-[#151515]/40 rounded-xl shadow-lg hover:shadow-2xl transition-shadow duration-300 hover:bg-[#202020]/50 cursor-pointer flex flex-col items-center gap-y-5"
                            >
                                <p className="text-[#FAFAFA] text-2xl font-bold">Transformers</p>
                                <p className="text-[#FAFAFA] text-xl">Architecture behind LLMs</p>
                            </a>

                            <a
                                href="https://arxiv.org/pdf/2401.08281"
                                target="_blank"
                                rel="faiss_article"
                                className="max-w-sm p-6 bg-[#151515]/40 rounded-xl shadow-lg hover:shadow-2xl transition-shadow duration-300 hover:bg-[#202020]/50 cursor-pointer flex flex-col items-center gap-y-5"
                            >
                                <p className="text-[#FAFAFA] text-2xl font-bold">FAISS</p>
                                <p className="text-[#FAFAFA] text-xl">Facebook AI Similarity Search</p>
                            </a>
                        </div>

                    </main>
                )}

                {isModalReferencesOpen && (
                    <div
                        className="fixed inset-0 flex items-center justify-center z-50 backdrop-blur-md bg-black/10"
                        onClick={() => setIsModalReferencesOpen(false)}
                    >
                        <div
                            className="bg-[#242424] max-w-2xl w-full rounded-lg shadow-lg p-6 overflow-y-auto max-h-[80vh] relative scrollbar"
                            onClick={(e) => e.stopPropagation()}
                        >
                            <button
                                className="absolute top-2 right-3 text-[#FAFAFA] hover:text-gray-300"
                                onClick={() => setIsModalReferencesOpen(false)}
                            >
                                <span className="text-xl">&times;</span>
                            </button>

                            <h2 className="text-xl font-semibold mb-4 text-[#FAFAFA]">References found</h2>

                            <div className="space-y-4">
                                {modalReferences.map((ref, idx) => (
                                    <div key={idx}>
                                        <p className="text-sm text-[#FAFAFA] whitespace-pre-wrap">
                                            {ref.content.trim()}
                                        </p>
                                        <p className="text-purple-500 text-xs font-medium mt-2">
                                            Similarity:&nbsp;
                                            <span className="text-xs text-[#FAFAFA] font-medium mt-2">{ref.similarity.toFixed(4)}</span>
                                            &nbsp;
                                        </p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}
            </MainContainer>
        </div>
    );
}
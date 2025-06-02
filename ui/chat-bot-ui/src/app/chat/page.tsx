"use client";

import { useState, useEffect, useRef } from "react";
import MainContainer from "@/components/main-container";
import Sidebar from "@/components/chat-sidebar";
import { TypingEffect } from "@/components/typing-effect";
import { FiSend } from "react-icons/fi";
import { getMessages, Message, getAnswer, createMessage } from "@/services/model";

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
                            <p className="text-white text-2xl">Carregando mensagens...</p>
                        </main>
                    ) : messages && messages.length > 0 ? (
                        <div className="flex flex-col ">
                            <div className="space-y-4 px-90 py-20 h-[80vh] overflow-y-auto">
                                {messages.map((msg, index) => {
                                    let content = null;
                                    let references = [];

                                    try {
                                        const parsed =
                                            typeof msg.text === "string" ? JSON.parse(msg.text) : msg.text;
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
                                                <div className="max-w-[70%] bg-[#313131] text-white p-3 rounded-2xl shadow whitespace-pre-wrap">
                                                    {content}
                                                </div>
                                            </div>
                                        );
                                    }

                                    return (
                                        <div key={index} className="flex justify-start">
                                            <div className="max-w-[70%] bg-[#242424] text-white p-3 rounded-2xl whitespace-pre-wrap">
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
                                                                        {' <\\'}
                                                                        <a
                                                                            href="#"
                                                                            onClick={(e) => {
                                                                                e.preventDefault();
                                                                                console.log("nada ainda");
                                                                            }}
                                                                            className="text-purple-600 hover:underline"
                                                                        >
                                                                            See references
                                                                        </a>
                                                                        {'>'}
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

                            <div ref={bottomRef} />

                            <div className="flex items-center justify-center w-full mx-auto gap-5">
                                <input
                                    type="text"
                                    className="flex-grow max-w-2xl px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                                    placeholder="Pergunte alguma coisa"
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
                                    className="w-10 h-10 bg-purple-600 hover:bg-purple-700 text-white rounded-full flex items-center justify-center transition-colors"
                                    onClick={handleSendSentence}
                                >
                                    <FiSend size={20} className="rotate-45" />
                                </button>
                            </div>

                            <div className="items-center justify-center">
                                <p className="text-gray-600">
                                    Este projeto utiliza como base de dados{" "}
                                    <a
                                        href="https://huggingface.co/datasets/habedi/stack-exchange-dataset"
                                        onClick={(e) => console.log("nada ainda")}
                                        className="text-purple-600 hover:underline"
                                    >
                                        habedi/stack-exchange-dataset
                                    </a>
                                    .
                                </p>
                            </div>
                        </div>
                    ) : (

                        <main className="min-h-screen flex flex-col items-center justify-center gap-y-5">
                            <div className="flex flex-row items-center gap-x-5">
                                <h1 className="text-white text-6xl font-semibold">Como posso ajudar?</h1>
                                <img
                                    src="/chatbot_logo.png"
                                    width={200}
                                    height={200}
                                    alt="Logo do Chatbot"
                                />
                            </div>

                            <div className="flex items-center justify-center w-full mx-auto gap-5">
                                <input
                                    type="text"
                                    className="flex-grow max-w-2xl px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                                    placeholder="Pergunte alguma coisa"
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
                                    className="w-10 h-10 bg-purple-600 hover:bg-purple-700 text-white rounded-full flex items-center justify-center transition-colors"
                                    onClick={handleSendSentence}
                                >
                                    <FiSend size={20} className="rotate-45" />
                                </button>
                            </div>

                            <p className="text-gray-600">
                                Este projeto utiliza como base de dados{' '}
                                <a href="https://huggingface.co/datasets/habedi/stack-exchange-dataset" onClick={(e) => console.log('nada ainda')} className="text-purple-600 hover:underline">
                                    habedi/stack-exchange-dataset
                                </a>
                                .
                            </p>
                        </main>
                    )

                ) : (

                    <main className="min-h-screen flex flex-col items-center justify-center gap-y-15">
                        <div className="flex flex-row items-center gap-x-5">
                            <h1 className="text-white text-6xl font-semibold">ChatBot</h1>
                            <img
                                src="/chatbot_logo.png"
                                width={200}
                                height={200}
                                alt="Logo do Chatbot"
                            />
                        </div>

                        <p className="text-white text-4xl text-center max-w-5xl">
                            A base de dados deste projeto possui informações das áreas de&nbsp;
                            <span className="text-purple-500">Ciência da Computação</span>
                            &nbsp;e&nbsp;
                            <span className="text-purple-500">Ciência de Dados</span>.
                        </p>

                        <p className="text-white text-4xl text-center max-w-xl">
                            Comece criando um <span className="text-purple-500">Novo Chat</span>.
                        </p>

                        <p className="text-white text-2xl text-center max-w-xl">
                            Veja também:
                        </p>

                        <div className="flex flex-row items-center gap-x-5">
                            <a
                                href="https://arxiv.org/pdf/1706.03762"
                                target="_blank"
                                rel="transformers_article"
                                className="max-w-sm p-6 bg-[#151515]/40 rounded-xl shadow-lg hover:shadow-2xl transition-shadow duration-300 hover:bg-[#202020]/50 cursor-pointer flex flex-col items-center gap-y-5"
                            >
                                <p className="text-white text-2xl font-bold">Transformers</p>
                                <p className="text-white text-xl">Architecture behind LLMs</p>
                            </a>

                            <a
                                href="https://arxiv.org/pdf/2401.08281"
                                target="_blank"
                                rel="faiss_article"
                                className="max-w-sm p-6 bg-[#151515]/40 rounded-xl shadow-lg hover:shadow-2xl transition-shadow duration-300 hover:bg-[#202020]/50 cursor-pointer flex flex-col items-center gap-y-5"
                            >
                                <p className="text-white text-2xl font-bold">FAISS</p>
                                <p className="text-white text-xl">Facebook AI Similarity Search</p>
                            </a>
                        </div>

                    </main>
                )}
            </MainContainer>
        </div>
    );
}
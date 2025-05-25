"use client";

import { useState, useEffect } from "react";
import MainContainer from "@/components/main-container";
import Sidebar from "@/components/chat-sidebar";
import { FiSend } from "react-icons/fi";
import { getMessages, Message } from "@/services/model";

export default function ChatPage() {
    const [selectedChatId, setSelectedChatId] = useState<number | null>(null);
    const [messages, setMessages] = useState<Message[] | null>(null);
    const [loadingMessages, setLoadingMessages] = useState(false);

    useEffect(() => {
        const fetchMessages = async () => {
            if (selectedChatId !== null) {
                setLoadingMessages(true);

                try {
                    const msgs = await getMessages(selectedChatId);
                    setMessages(msgs);

                } catch (err) {
                    console.error("Erro ao carregar mensagens:", err);
                    setMessages([]);

                } finally {
                    setLoadingMessages(false);
                }

            } else {
                setMessages(null);
            }
        };

        fetchMessages();
    }, [selectedChatId]);

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
                        <main className="min-h-screen flex flex-col items-center justify-center gap-y-4">
                            <h1 className="text-white text-4xl font-bold">Chat #{selectedChatId}</h1>
                            {/* Aqui você renderiza as mensagens */}
                            <ul className="text-white space-y-2">
                                {messages.map((msg) => (
                                    <li key={msg.id} className={msg.is_user ? "text-right" : "text-left"}>
                                        {msg.text}
                                    </li>
                                ))}
                            </ul>
                        </main>
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
                                    onChange={(e) => console.log("nada ainda")}
                                />

                                <button
                                    type="button"
                                    className="w-10 h-10 bg-purple-600 hover:bg-purple-700 text-white rounded-full flex items-center justify-center transition-colors"
                                    onClick={() => console.log("Enviar")}
                                >
                                    <FiSend size={20} className="rotate-45" />
                                </button>
                            </div>

                            <p className="text-gray-600">
                                Este projeto utiliza como base de dados{' '}
                                <a href="#" onClick={(e) => console.log('nada ainda')} className="text-purple-600 hover:underline">
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
        </div >
    );
}
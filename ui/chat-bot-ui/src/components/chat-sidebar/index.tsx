"use client"

import { useEffect, useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { FiSettings, FiTrash2 } from 'react-icons/fi';
import { logout } from '@/services/auth';
import { Chat, getAllChats, createChat, deleteChat, groupChatsByDate } from '@/services/model';
import '../../styles/globals.css';

export default function Sidebar() {
    const router = useRouter();

    const [chats, setChats] = useState<Chat[]>([]);
    const [loading, setLoading] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [newChatName, setNewChatName] = useState('');

    useEffect(() => {
        const fetchChats = async () => {
            try {
                const data = await getAllChats();

                setChats(data);

            } catch (error) {
                console.error(error);

            } finally {
                setLoading(false);
            }
        };

        fetchChats();
    }, []);

    const grouped = useMemo(() => groupChatsByDate(chats), [chats]);

    const groupTitleMap: Record<string, string> = {
        today: "Today",
        yesterday: "Yesterday",
        last7Days: "last 7 days",
        older: "Oldest chats",
    };

    const handleCreateChat = async () => {
        try {
            await createChat(newChatName.trim());

            const updatedChats = await getAllChats();

            setChats(updatedChats);
            setIsModalOpen(false);
            setNewChatName('');

        } catch (error) {
            console.error("Error creating chat:", error);
        }
    };

    const handleLogout = async () => {
        await logout();

        router.push('/login');
    };

    const handleSettings = () => {
        router.push('/settings');
    };

    const handleDeleteChat = async (chatId: number) => {
        try {
            const success = await deleteChat(chatId);
            if (success) {
                setChats((prevChats) => prevChats.filter((chat) => chat.id !== chatId));
            }
        } catch (error) {
            console.error("Error deleting chat:", error);
        }
    };

    return (
        <>
            {isModalOpen && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-[#1e1e1e] p-6 rounded-lg w-[90%] max-w-md shadow-lg">
                        <h2 className="text-white text-xl mb-4">New chat</h2>
                        <input
                            type="text"
                            placeholder="Chat name"
                            value={newChatName}
                            onChange={(e) => setNewChatName(e.target.value)}
                            className="w-full p-2 mb-4 rounded bg-[#2c2c2c] text-white border border-gray-700 focus:outline-none"
                        />
                        <div className="flex justify-end gap-4">
                            <button
                                onClick={() => {
                                    setIsModalOpen(false);
                                    setNewChatName('');
                                }}
                                className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleCreateChat}
                                className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700"
                            >
                                Create
                            </button>
                        </div>
                    </div>
                </div>
            )}


            <div className="w-64 h-screen bg-[#100F10] border-r flex flex-col py-4 px-4">

                <div className="flex-1 overflow-y-auto px-4 pr-5 scrollbar">

                    <div className="mb-4">
                        <button
                            onClick={() => setIsModalOpen(true)}
                            className="w-full bg-[#242424] text-white py-2 px-4 rounded hover:bg-purple-700 transition flex items-center justify-center gap-2"
                        >
                            <img src="/chatbot_logo.png" alt="New Chat" className="w-10 h-10" />
                            New Chat
                        </button>

                    </div>

                    <div className="h-4" />

                    {loading ? (
                        <p className="text-white text-center mt-8">Loading...</p>
                    ) : chats.length === 0 ? (
                        <p className="text-white text-center mt-8">No chat found.</p>
                    ) : (
                        Object.entries(grouped).map(([group, groupChats]) =>
                            groupChats.length > 0 && (
                                <div key={group} className="mb-6">
                                    <h3 className="text-white font-semibold mb-2">{groupTitleMap[group]}</h3>
                                    {groupChats.map((chat) => (
                                        <div
                                            key={chat.id}
                                            className="py-4 px-4 bg-[#242424] rounded-xl hover:bg-[#303030] cursor-pointer mb-4 flex justify-between items-center"
                                        >
                                            <span>{chat.chat_name}</span>
                                            <button
                                                onClick={(e) => {
                                                    e.stopPropagation();

                                                    handleDeleteChat(chat.id);
                                                }}
                                                className="text-red-500 hover:text-red-700"
                                                aria-label={`Delete chat ${chat.chat_name}`}
                                                title="Delete chat"
                                            >
                                                <FiTrash2 size={18} />
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            )
                        )
                    )}
                </div>

                <div className="p-4 border-t">
                    <div className="flex gap-2">
                        <button
                            className="w-full bg-red-600 text-white py-2 px-4 rounded hover:bg-red-700 transition"
                            onClick={handleLogout}
                        >
                            Logout
                        </button>

                        <button
                            onClick={handleSettings}
                            title="Settings"
                            className="text-white hover:text-purple-500 transition"
                        >
                            <FiSettings size={22} />
                        </button>
                    </div>
                </div>
            </div>
        </>

    );
}
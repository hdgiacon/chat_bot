"use client"

import { useEffect, useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { FiSettings, FiTrash2 } from 'react-icons/fi';
import { logout } from '@/services/auth';
import { read_user, update_user, delete_user } from '@/services/user';
import { Chat, getAllChats, createChat, deleteChat, groupChatsByDate } from '@/services/model';
import '../../styles/globals.css';

export default function Sidebar({ onSelectChat, selectedChatId, }: { onSelectChat: (chatId: number) => void; selectedChatId: number | null; }) {
    const router = useRouter();

    const [chats, setChats] = useState<Chat[]>([]);
    const [loading, setLoading] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [newChatName, setNewChatName] = useState('');

    const [isModalSettingsOpen, setIsModalSettingsOpen] = useState(false);
    const [firstName, setFirstName] = useState('');
    const [lastName, setLastName] = useState('');
    const [email, setEmail] = useState('');

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
            const chat = await createChat(newChatName.trim());
            const updatedChats = await getAllChats();
            setChats(updatedChats);
            setIsModalOpen(false);
            setNewChatName('');
            onSelectChat(chat.id);
        } catch (error) {
            console.error("Error creating chat:", error);
        }
    };

    const handleLogout = async () => {
        await logout();
        router.push('/login');
    };

    const handleSettingsModal = () => {
        setIsModalSettingsOpen(true);
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

    useEffect(() => {
        const fetchUserData = async () => {
            try {
                const data = await read_user();

                setFirstName(data.first_name);
                setLastName(data.last_name);
                setEmail(data.email);

            } catch (error) {
                console.error("Erro ao carregar dados do usuário:", error);
            }
        };

        if (isModalSettingsOpen) {
            fetchUserData();
        }
    }, [isModalSettingsOpen]);

    const handleUpdate = async () => {
        try {
            await update_user(firstName, lastName, email);

            alert("Dados atualizados com sucesso!");
            setIsModalSettingsOpen(false);

        } catch (error) {
            console.error("Erro ao atualizar usuário:", error);

            alert("Erro ao atualizar os dados. Tente novamente.");
        }
    };

    const handleDelete = async () => {
        const confirmed = window.confirm("Tem certeza que deseja deletar sua conta? Esta ação é irreversível.");

        if (!confirmed) return;

        try {
            await delete_user();

            alert("Conta deletada com sucesso!");

            router.push('/login');

        } catch (error) {
            console.error("Erro ao deletar usuário:", error);

            alert("Erro ao deletar a conta. Tente novamente.");
        }
    };

    return (
        <>
            {isModalOpen && (
                <div
                    className="fixed inset-0 flex items-center justify-center z-50 backdrop-blur-md bg-black/10"
                    onClick={() => {
                        setIsModalOpen(false);
                        setNewChatName('');
                    }}
                >
                    <div
                        className="bg-[#1e1e1e] p-6 rounded-lg w-[90%] max-w-md shadow-lg"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <h2 className="text-[#FAFAFA] text-xl mb-4">New chat</h2>
                        <input
                            type="text"
                            placeholder="Chat name"
                            value={newChatName}
                            onChange={(e) => setNewChatName(e.target.value)}
                            className="w-full p-2 mb-4 rounded bg-[#2c2c2c] text-[#FAFAFA] border border-gray-700 focus:outline-none"
                        />
                        <div className="flex justify-end gap-4">
                            <button
                                onClick={() => {
                                    setIsModalOpen(false);
                                    setNewChatName('');
                                }}
                                className="px-4 py-2 bg-gray-600 text-[#FAFAFA] rounded hover:bg-gray-700"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleCreateChat}
                                className="px-4 py-2 bg-purple-600 text-[#FAFAFA] rounded hover:bg-purple-700"
                            >
                                Create
                            </button>
                        </div>
                    </div>
                </div>
            )}

            <div className="w-64 h-screen bg-[#1B1B1B] border-[#1B1B1B] border-r flex flex-col py-4 px-4">
                <div className="flex-1 overflow-y-auto px-4 pr-5 scrollbar">
                    <div className="mb-4">
                        <button
                            onClick={() => setIsModalOpen(true)}
                            className="w-full bg-[#242424] text-[#FAFAFA] py-2 px-4 rounded hover:bg-purple-900 transition flex items-center justify-center gap-2"
                        >
                            <img src="/chatbot_logo.png" alt="New Chat" className="w-10 h-10" />
                            New Chat
                        </button>
                    </div>

                    <div className="h-4" />

                    {loading ? (
                        <p className="text-[#FAFAFA] text-center mt-8">Loading...</p>
                    ) : chats.length === 0 ? (
                        <p className="text-[#FAFAFA] text-center mt-8">No chat found.</p>
                    ) : (
                        Object.entries(grouped).map(([group, groupChats]) =>
                            groupChats.length > 0 && (
                                <div key={group} className="mb-6">
                                    <h3 className="text-[#FAFAFA] font-semibold mb-2">{groupTitleMap[group]}</h3>
                                    {groupChats.map((chat) => (
                                        <div
                                            key={chat.id}
                                            className={`py-3 px-4 rounded-sm cursor-pointer mb-4 flex justify-between items-center transition-all gap-x-1 ${selectedChatId === chat.id
                                                ? "bg-[#3f3f3f]"
                                                : "bg-[#242424] hover:bg-[#303030]"
                                                }`}
                                            onClick={() => onSelectChat(chat.id)}
                                        >
                                            <span className="text-[#FAFAFA] truncate text-sm">{chat.chat_name}</span>
                                            <button
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    handleDeleteChat(chat.id);
                                                }}
                                                className="text-gray-500 hover:text-red-700"
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

                <div className="p-4 border-t border-[#1B1B1B]">
                    <div className="flex gap-2">
                        <button
                            className="w-full bg-red-700 text-[#FAFAFA] py-2 px-4 rounded hover:bg-red-800 transition"
                            onClick={handleLogout}
                        >
                            Logout
                        </button>

                        <button
                            onClick={(e) => {
                                e.preventDefault();
                                handleSettingsModal();
                            }}
                            title="Settings"
                            className="text-[#FAFAFA] hover:text-purple-700 transition"
                        >
                            <FiSettings size={22} />
                        </button>
                    </div>
                </div>
            </div>

            {isModalSettingsOpen && (
                <div
                    className="fixed inset-0 flex items-center justify-center z-50 backdrop-blur-md bg-black/10"
                    onClick={() => setIsModalSettingsOpen(false)}
                >
                    <div
                        className="bg-[#242424] max-w-2xl w-full rounded-lg shadow-lg p-6 overflow-y-auto max-h-[90vh]"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <h1 className="text-3xl font-bold text-center text-[#FAFAFA] mb-6">Settings</h1>

                        <div className="h-5" />

                        <div className="space-y-4 max-w-md mx-auto">

                            <p className="text-[#ff9100] text-lg font-medium">
                                Update&nbsp;
                                <span className="text-[#FAFAFA] font-medium">my account</span>
                            </p>

                            <input
                                type="text"
                                placeholder="First name"
                                value={firstName}
                                onChange={(e) => setFirstName(e.target.value)}
                                className="w-full px-4 py-2 border border-transparent rounded-md bg-[#313131] focus:outline-none focus:ring-1 focus:ring-purple-800"
                            />

                            <input
                                type="text"
                                placeholder="Last name"
                                value={lastName}
                                onChange={(e) => setLastName(e.target.value)}
                                className="w-full px-4 py-2 border border-transparent rounded-md bg-[#313131] focus:outline-none focus:ring-1 focus:ring-purple-800"
                            />

                            <input
                                type="text"
                                placeholder="Email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="w-full px-4 py-2 border border-transparent rounded-md bg-[#313131] focus:outline-none focus:ring-1 focus:ring-purple-800"
                            />

                            <div className="h-3" />

                            <button
                                className="w-full py-2 bg-[#ff9100] text-[#FAFAFA] rounded-md hover:bg-[#ff6600]"
                                onClick={handleUpdate}
                            >
                                Update
                            </button>

                            <button
                                className="w-full py-2 bg-[#303030] text-[#FAFAFA] rounded-md hover:bg-[#353535]"
                                onClick={() => setIsModalSettingsOpen(false)}
                            >
                                Back
                            </button>

                            <div className="h-4" />

                            <p className="text-red-600 text-lg font-medium">
                                Delete&nbsp;
                                <span className="text-[#FAFAFA] font-medium">my account</span>
                            </p>

                            <button
                                className="w-full py-2 bg-red-700 text-[#FAFAFA] rounded-md hover:bg-red-800"
                                onClick={handleDelete}
                            >
                                Delete
                            </button>

                            <div className="h-2" />
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}

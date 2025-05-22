"use client"

import { useRouter } from 'next/navigation';
import { logout } from "@/services/auth";
import '../../styles/globals.css';

export default function Sidebar() {
    const router = useRouter();

    const handleLogout = async () => {
        await logout();

        router.push('/login');
    };

    return (
        <div className="w-64 h-screen bg-[#100F10] border-r flex flex-col py-4 px-4">
            <div className="p-4 border-b">
                <button className="w-full bg-[#242424] text-white py-2 px-4 rounded hover:bg-purple-700 transition flex items-center justify-center gap-2">
                    <img
                        src="/chatbot_logo.png"
                        alt="New Chat"
                        className="w-10 h-10"
                    />
                    New Chat
                </button>
            </div>

            <div className="h-screen p-4 overflow-y-auto scrollbar">
                {Array.from({ length: 20 }).map((_, i) => (
                    <div
                        key={i}
                        className="py-4 px-4 bg-[#242424] rounded-xl hover:bg-[#303030] cursor-pointer mb-4"
                    >
                        Conversa {i + 1}
                    </div>
                ))}
            </div>

            <div className="p-4 border-b">
                <button className="w-full bg-red-600 text-white py-2 px-4 rounded hover:bg-red-700 transition" onClick={handleLogout}>
                    Logout
                </button>
            </div>

            {/* TODO: colocar icone de settings ao lado do botão de logout */}
        </div>
    );
}
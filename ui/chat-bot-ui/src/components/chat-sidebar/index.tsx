import '../../styles/globals.css';

export default function Sidebar() {
    return (
        <div className="w-64 h-screen bg-[#100F10] border-r flex flex-col py-4 px-4">
            <div className="p-4 border-b">
                <button className="w-full bg-purple-600 text-white py-2 px-4 rounded hover:bg-purple-700 transition">
                    Novo Chat
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
                <button className="w-full bg-red-600 text-white py-2 px-4 rounded hover:bg-red-700 transition">
                    Logout
                </button>
            </div>
        </div>
    );
}
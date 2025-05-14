import MainContainer from "@/components/main-container";
import Sidebar from "@/components/chat-sidebar";

export default function ChatPage() {
    return (
        <MainContainer>
            <Sidebar />
            <main className="flex-1 p-4">
                {/* Conteúdo principal */}
            </main>
        </MainContainer>
    );
}
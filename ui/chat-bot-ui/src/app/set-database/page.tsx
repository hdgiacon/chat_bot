'use client';

import { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import MainContainer from "@/components/main-container";
import { monitorTraining } from '@/services/model';

export default function SetDatabase() {
    const router = useRouter();

    const [statusMessage, setStatusMessage] = useState("Starting");
    const [progress, setProgress] = useState(0);
    const [showButton, setShowButton] = useState(false);
    const previousResultRef = useRef("");

    const progressStages: { [key: string]: number } = {
        "Starting": 0,
        "Downloading data from HuggingFace": 25,
        "Setting data on Postgre database": 50,
        "Creating embeddings and vector base": 75,
        "Creating FAISS vector base success": 100
    };

    useEffect(() => {
        const interval = setInterval(async () => {
            try {
                const { status, result } = await monitorTraining();

                setStatusMessage(result);

                if (result !== previousResultRef.current && result in progressStages) {
                    setProgress(progressStages[result]);
                    previousResultRef.current = result;
                }

                if (status === 'SUCCESS') {
                    setProgress(100);
                    setShowButton(true);
                    clearInterval(interval);
                }

                if (status === 'FAILURE') {
                    clearInterval(interval);
                }

            } catch (err) {
                console.error("Erro ao verificar status da task:", err);
                clearInterval(interval);
            }
        }, 5000);

        return () => clearInterval(interval);
    }, []);

    const handleChat = () => {
        router.push('/chat');
    };

    return (
        <MainContainer>
            <div className="flex w-full h-screen">

                <div className="w-1/3 p-15 flex flex-col justify-center items-start space-y-2">
                    <h1 className="text-5xl font-semibold mb-6">
                        <span className="text-[#FAFAFA]">Downloading</span>{' '}
                        <span className="text-purple-900">dataset</span>
                    </h1>

                    <h1 className="text-5xl font-semibold text-purple-900 mb-6">and</h1>

                    <h1 className="text-5xl font-semibold mb-6">
                        <span className="text-[#FAFAFA]">training</span>{' '}
                        <span className="text-purple-900">model</span>
                    </h1>

                    <div className="h-4" />

                    <p className="text-[#FAFAFA]">
                        This may take a while. In the meantime, you can check which models are used on this project:{" "}
                        <a
                            href="https://ai.google.dev/gemini-api/docs/models?hl=pt-br#gemini-1.5-flash"
                            className="text-purple-900 hover:underline"
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            Gemini
                        </a>{" "}
                        and{" "}
                        <a
                            href="https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2"
                            className="text-purple-900 hover:underline"
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            all-MiniLM-L6-v2
                        </a>
                        .
                    </p>
                </div>

                <div className="w-2/3 p-4 flex flex-col items-center justify-center">
                    <div className="relative animate-pulse mb-12">
                        <img src="/cloud.png" alt="Cloud" className="w-90 h-auto" />
                        <img
                            src="/arrow.png"
                            alt="Arrow Down"
                            className="absolute left-1/2 -translate-x-1/2 bottom-0 w-40 h-auto"
                        />
                    </div>

                    <div className="w-2/3 bg-gray-300 rounded-full h-2 overflow-hidden mb-4">
                        <div
                            className="bg-purple-600 h-full transition-all duration-500"
                            style={{ width: `${progress}%` }}
                        ></div>
                    </div>

                    <p className="text-[#FAFAFA] text-lg text-center flex items-center justify-center gap-2">
                        {statusMessage}
                        {statusMessage !== "Creating FAISS vector base success" ? (
                            <span className="animate-pulse">...</span>
                        ) : (
                            <span className="text-purple-900">✔</span>
                        )}
                    </p>

                    <div className="h-4" />

                    {showButton && (
                        <button
                            className="mt-6 px-6 py-3 bg-purple-900 text-[#FAFAFA] rounded-lg hover:bg-purple-950 transition duration-300"
                            onClick={handleChat}
                        >
                            Start chat
                        </button>
                    )}
                </div>
            </div>
        </MainContainer>
    );
}
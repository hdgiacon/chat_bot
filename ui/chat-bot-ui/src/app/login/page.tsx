'use client'

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import MainContainer from "@/components/main-container";
import { login } from "@/services/auth";
import { trainModel } from '@/services/model';

export default function LoginPage() {
    const router = useRouter();

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    const handleLogin = async () => {
        await login(email, password);

        const must_train_model = await trainModel();

        if (must_train_model) {
            router.push('/set-database');

        }

        else {
            router.push('/chat');
        }

    };

    const handleSignUp = (e: React.MouseEvent<HTMLAnchorElement>) => {
        e.preventDefault();

        router.push('/sign-up');
    };

    return (
        <MainContainer>
            <div className="relative flex min-h-screen w-full overflow-hidden">

                <div className="w-1/2 flex flex-col items-center justify-center p-8">
                    <h2 className="text-3xl font-semibold text-purple-600 mb-6">Sign in</h2>

                    <div className="w-full max-w-md space-y-4">
                        <input
                            type="text"
                            className="w-full px-4 py-2 border border-transparent rounded-md bg-[#313131] bg-opacity-10 focus:outline-none focus:ring-1 focus:ring-purple-800"
                            placeholder="Email"
                            onChange={(e) => setEmail(e.target.value)}
                        />

                        <input
                            type="password"
                            className="w-full px-4 py-2 border border-transparent rounded-md bg-[#313131] bg-opacity-10 focus:outline-none focus:ring-1 focus:ring-purple-800"
                            placeholder="Password"
                            onChange={(e) => setPassword(e.target.value)}
                        />

                        <div className="h-4" />

                        <button className="w-full py-2 bg-purple-800 text-[#FAFAFA] rounded-md hover:bg-purple-900" onClick={handleLogin}>
                            Login
                        </button>

                        <div className="text-center mt-4">
                            <p className="text-gray-600">
                                Don't have an account?{' '}
                                <a href="#" onClick={handleSignUp} className="text-purple-600 hover:underline">
                                    Sign up here
                                </a>
                            </p>
                        </div>
                    </div>
                </div>

                <div className="w-1/2 relative flex items-center justify-center">
                    <img
                        src="/ai_gif.gif"
                        alt="Animação"
                        className="object-cover w-full h-full filter grayscale opacity-10"
                        style={{
                            maskImage: 'linear-gradient(to right, rgba(0,0,0,0) 0%, rgba(0,0,0,1) 20%, rgba(0,0,0,1) 50%, rgba(0,0,0,1) 100%)'
                        }}
                    />
                </div>
            </div>
        </MainContainer>
    );
}
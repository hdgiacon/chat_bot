import { useState, useEffect } from "react";

interface TypingEffectProps {
    text: string;
    speed?: number;
    onFinish?: () => void;
}

export function TypingEffect({ text, speed = 20, onFinish }: TypingEffectProps) {
    const [displayedText, setDisplayedText] = useState("");

    useEffect(() => {
        setDisplayedText("");
        if (!text) return;

        let currentIndex = 0;
        const interval = setInterval(() => {
            setDisplayedText((prev) => prev + text[currentIndex]);
            currentIndex++;
            if (currentIndex === text.length) {
                clearInterval(interval);
                if (onFinish) onFinish();
            }
        }, speed);

        return () => clearInterval(interval);
    }, [text, speed, onFinish]);

    return <>{displayedText}</>;
}

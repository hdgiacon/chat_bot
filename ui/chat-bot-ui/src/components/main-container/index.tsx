import { ReactNode } from 'react';

export default function MainContainer({ children, sideCard }: { children: ReactNode; sideCard?: ReactNode }) {
    return (
        <div className="flex w-full flex-1 flex-col bg-[#242424]">
            <div className="grid grid-cols-12 lg:gap-10">
                <div className="col-span-12 h-fit ">
                    <div>{children}</div>
                </div>
            </div>
        </div>
    );
}
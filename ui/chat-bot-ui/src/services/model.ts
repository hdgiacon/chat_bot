export async function trainModel(){
    const access_token = localStorage.getItem("access_token");

    if (!access_token) {
        throw new Error("Token not found in localStorage");
    }
    
    try{
        const response = await fetch("http://localhost:8000/app_model/train/model/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${access_token}`,
            },
        });

        if (!response.ok) throw new Error("Train model failed");

        const data = await response.json();

        if ("task_id" in data) {
            localStorage.setItem('task_id', data['task_id'])

            return true;
        } 
        
        else {
            return false;
        }
    
    } catch (error) {
        console.error("Error in model training: ", error);
        
        throw error;
    }
}


export async function monitorTraining(): Promise<{ status: string; result: string }> {
    const access_token = localStorage.getItem("access_token");
    const task_id = localStorage.getItem("task_id");

    if (!access_token || !task_id) {
        throw new Error("Token or task_id not found in localStorage");
    }

    const response = await fetch("http://localhost:8000/app_model/monitor/training/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${access_token}`,
        },
        body: JSON.stringify({ task_id }),
    });

    if (!response.ok) throw new Error("Error fetching task status");

    const data = await response.json();

    return {
        status: data.status,
        result: data.result,
    };
}


// TODO: getAnswer


export type Chat = {
  id: number;
  chat_name: string;
  user_id: number;
  created_at: string;
};


export async function getAllChats(): Promise<Chat[]> {
    const access_token = localStorage.getItem("access_token");

    if (!access_token) {
        throw new Error("Token not found ino localStorage");
    }

    const response = await fetch("http://localhost:8000/app_model/chat/list/", {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${access_token}`,
        },
    });

    if (!response.ok) throw new Error("Train model failed");

    const data = await response.json();

    data.sort((a: Chat, b: Chat) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());

    return data;
}


export async function createChat(chat_name: string): Promise<Chat> {
    const access_token = localStorage.getItem("access_token");

    if (!access_token) {
        throw new Error("Token not found in localStorage");
    }

    if (chat_name.trim() === "") {
        throw new Error("Chat name must not be null");
    }

    try {
        const response = await fetch("http://localhost:8000/app_model/chat/create/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${access_token}`,
            },
            body: JSON.stringify({ chat_name }),
        });

        if (!response.ok) throw new Error("Create chat failed");

        const data: Chat = await response.json();
        
        return data;

    } catch (error) {
        console.error("Error creating chat: ", error);
        
        throw error;
    }
}


export async function deleteChat(chat_id: number): Promise<boolean> {
    const access_token = localStorage.getItem("access_token");

    if (!access_token) {
        throw new Error("Token not found in localStorage");
    }

    if (chat_id == undefined) {
        throw new Error("Chat id must not be null");
    }

    try{
        const response = await fetch(`http://localhost:8000/app_model/chat/${chat_id}/delete/`, {
            method: "DELETE",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${access_token}`,
            },
        });

        if (!response.ok) throw new Error("Delete chat failed");

        return true
    
    }catch (error) {
        console.error("Error deleting chat: ", error);
        
        throw error;
    }
}


export function groupChatsByDate(chats: Chat[]) {
    const grouped: {
        today: Chat[];
        yesterday: Chat[];
        last7Days: Chat[];
        older: Chat[];
    } = {
        today: [],
        yesterday: [],
        last7Days: [],
        older: [],
    };

    const now = new Date();

    chats.forEach((chat) => {
        const createdAt = new Date(chat.created_at);
        const diffTime = now.getTime() - createdAt.getTime();
        const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

        if (diffDays === 0) {
            grouped.today.push(chat);
        } else if (diffDays === 1) {
            grouped.yesterday.push(chat);
        } else if (diffDays <= 7) {
            grouped.last7Days.push(chat);
        } else {
            grouped.older.push(chat);
        }
    });

    return grouped;
}


export type Message = {
  id: number;
  text: string;
  is_user: boolean;
  created_at: string;
  chat_id: number;
};


export async function getMessages(chat_id: number): Promise<Message[]>{
    const access_token = localStorage.getItem("access_token");

    if (!access_token) {
        throw new Error("Token not found in localStorage");
    }

    if (chat_id == undefined) {
        throw new Error("Chat id must not be null");
    }

    try{
        const response = await fetch(`http://localhost:8000/app_model/message/${chat_id}/list/`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${access_token}`,
            },
        });

        if (!response.ok) throw new Error("Delete chat failed");

        const data = await response.json();

        return data
    
    } catch (error) {
        console.error("Error deleting chat: ", error);
        
        throw error;
    }
}
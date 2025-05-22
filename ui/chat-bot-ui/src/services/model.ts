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
        console.error("Erro no treinamento do modelo: ", error);
        
        throw error;
    }
}


export async function monitorTraining(): Promise<{ status: string; result: string }> {
    const access_token = localStorage.getItem("access_token");
    const task_id = localStorage.getItem("task_id");

    if (!access_token || !task_id) {
        throw new Error("Token ou task_id não encontrados no localStorage");
    }

    const response = await fetch("http://localhost:8000/app_model/monitor/training/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${access_token}`,
        },
        body: JSON.stringify({ task_id }),
    });

    if (!response.ok) {
        throw new Error("Erro ao buscar status da task");
    }

    const data = await response.json();

    return {
        status: data.status,
        result: data.result,
    };
}
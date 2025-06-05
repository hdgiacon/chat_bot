export async function create_user(first_name: string, last_name: string, email: string, password: string){
    const payload = { first_name, last_name, email, password }

    try{
        const response = await fetch("http://localhost:8000/user/create/", {
            method: "POST",
            headers: {
            "Content-Type": "application/json",
            },
            body: JSON.stringify(payload),
        });

        if (!response.ok) throw new Error("Create user failed");

        const data = await response.json();

        return data;
    
    } catch(error){
        console.error("Create user error: ", error)

        throw error;
    }
}


export async function read_user(){
    const access_token = localStorage.getItem("access_token");

    if (!access_token) {
        throw new Error("Token not found in localStorage");
    }

    try{
        const response = await fetch("http://localhost:8000/user/read/", {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${access_token}`,
            },
        });

        if (!response.ok) throw new Error("Read user failed");

        const data = await response.json();

        return data;
    
    } catch(error){
        console.error("Read user error: ", error)

        throw error;
    }
}

// TODO: se todos os campos não forem modificados, da um erro
export async function update_user(first_name: string, last_name: string, email: string){
    const access_token = localStorage.getItem("access_token");

    if (!access_token) {
        throw new Error("Token not found in localStorage");
    }
    
    const payload = { first_name, last_name, email }

    try{
        const response = await fetch("http://localhost:8000/user/update/", {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${access_token}`,
            },
            body: JSON.stringify(payload),
        });

        if (!response.ok) throw new Error("Update user failed");

        const data = await response.json();

        return data;
    
    } catch(error){
        console.error("Update user error: ", error)

        throw error;
    }
}


export async function delete_user(){
    const access_token = localStorage.getItem("access_token");

    if (!access_token) {
        throw new Error("Token not found in localStorage");
    }
    
    try{
        const response = await fetch("http://localhost:8000/user/delete/", {
            method: "DELETE",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${access_token}`,
            },
        });

        if (!response.ok) throw new Error("Delete user failed");
    
    } catch(error){
        console.error("Delete user error: ", error)

        throw error;
    }
}
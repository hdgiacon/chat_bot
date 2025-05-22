export async function sign_up(first_name: string, last_name: string, email: string, password: string){
    const payload = { first_name, last_name, email, password }

    try{
        const response = await fetch("http://localhost:8000/user/create/", {
            method: "POST",
            headers: {
            "Content-Type": "application/json",
            },
            body: JSON.stringify(payload),
        });

        if (!response.ok) throw new Error("Sign up failed");

        const data = await response.json();

        return data;
    
    } catch(error){
        console.error("Sign up error: ", error)

        throw error;
    }
}
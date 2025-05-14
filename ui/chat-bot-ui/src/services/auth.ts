export async function login(username: string, password: string) {
    const payload = { username, password };
  
    try {
      const response = await fetch("http://localhost:8000/app_auth/login/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });
  
      if (!response.ok) throw new Error("Login failed");
  
      const data = await response.json();
  
      localStorage.setItem("access_token", data.access);
      localStorage.setItem("refresh_token", data.refresh);
  
      return data;
    } catch (error) {
      console.error("Erro no login:", error);
      throw error;
    }
  }
  
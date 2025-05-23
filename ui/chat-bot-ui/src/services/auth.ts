export async function login(email: string, password: string) {
  const payload = { email, password };

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
    console.error("Login error: ", error);
    
    throw error;
  }
}
  

export async function logout() {
  const access_token = localStorage.getItem("access_token");
  const refresh_token = localStorage.getItem("refresh_token");

  if (!access_token || !refresh_token) {
    throw new Error("Tokens not found in localStorage");
  }

  const payload = { refresh: refresh_token };

  try {
    const response = await fetch("http://localhost:8000/app_auth/logout/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${access_token}`,
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) throw new Error("Logout failed");

    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");

  } catch (error) {
    console.error("Logout error: ", error);
    
    throw error;
  }
}
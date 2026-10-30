const API_BASE = "http://localhost:5002"

async function request(path, {method = 'GET', body = undefined, auth = false} = {}){
    const headers = {'Content-Type': 'application/json'}
    const token = localStorage.getItem("access_token")
    // Get the auth header
    if (auth && token){
        headers.Authorization = `Bearer ${token}`;
    }

    // Here we preform the fetch
    const resp = await fetch(`${API_BASE}/${path}`,
        {
            method: method,
            headers: headers,
            body: body ? JSON.stringify(body) : undefined
        }
    )

    // Here we gaurd against possible complications
    if (!resp.ok){
        const errData = await resp.json().catch(() => null);
        throw new Error(errData?.error || `Request failed with status ${resp.status}`);
    }

    // Here we return the response
    return resp.json();
}

export const api = {
    func_name: () => {return "Dummy Request"},
    register: (username, password) => request('register', { method: 'POST', body: { username, password } }),
    login: (username, password) => request('login', { method: 'POST', body: { username, password } }),
    me: () => request('me', {method: 'GET', body: undefined, auth: true}),

    getClub: (clubId) => request(`clubs/${clubId}`, { method: 'GET', body: undefined }),
    createClub: (club) => request('clubs', { method: 'POST', body: club }),
    updateClub: (clubId, updates) => request(`clubs/${clubId}`, { method: 'PATCH', body: updates }),
    deleteClub: (clubId) => request(`clubs/${clubId}`, { method: 'DELETE', body: undefined })
}


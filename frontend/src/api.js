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
    // Authentication and testing
    func_name: () => {return "Dummy Request"},
    register: (username, password) => request('register', { method: 'POST', body: { username, password } }),
    login: (username, password) => request('login', { method: 'POST', body: { username, password } }),
    me: () => request('me', {method: 'GET', body: undefined, auth: true}),

    // Clubs
    getClubs: () => request('clubs', { method: 'GET', body: undefined }),
    getClub: (clubId) => request(`clubs/${clubId}`, { method: 'GET', body: undefined }),
    createClub: (club) => request('clubs', { method: 'POST', body: club }),
    updateClub: (clubId, updates) => request(`clubs/${clubId}`, { method: 'PATCH', body: updates }),
    deleteClub: (clubId) => request(`clubs/${clubId}`, { method: 'DELETE', body: undefined }),

    // Regular Club Meetings
    getClubRegularMeetings: (clubId) => request(`clubs/${clubId}/regular-meetings`, { method: 'GET', body: undefined }),
    getClubRegularMeeting: (clubId, meetingId) => request(`clubs/${clubId}/regular-meetings/${meetingId}`, { method: 'GET', body: undefined }),
    createClubRegularMeeting: (clubId, meeting) => request(`clubs/${clubId}/regular-meetings`, { method: 'POST', body: meeting }),
    updateClubRegularMeeting: (clubId, meetingId, updates) => request(`clubs/${clubId}/regular-meetings/${meetingId}`, { method: 'PATCH', body: updates }),
    deleteClubRegularMeeting: (clubId, meetingId) => request(`clubs/${clubId}/regular-meetings/${meetingId}`, { method: 'DELETE', body: undefined }),

    // Saved Clubs
    getSavedClubs: () => request('saved-clubs', { method: 'GET', body: undefined, auth: true }),
    saveClub: (clubId) => request(`saved-clubs/${clubId}`, { method: 'POST', body: undefined, auth: true }),
    unsaveClub: (clubId) => request(`saved-clubs/${clubId}`, { method: 'DELETE', body: undefined, auth: true }),
  
    // Club Events
    getEvent: (eventId) => request(`event/select/${eventId}`, { method: 'GET', body: undefined }),
    getClubEvents: (clubId) => request(`event/${clubId}/select_all`, { method: 'GET', body: undefined }),
    createEvent: (clubId, event) => request(`event/create/${clubId}`, { method: 'POST', body: event, auth: true }),
    updateEvent: (eventId, updates) => request(`event/update/${eventId}`, { method: 'PATCH', body: updates, auth: true }),
    deleteEvent: (eventId) => request(`event/delete/${eventId}`, { method: 'DELETE', body: undefined, auth: true }),
    
    //Club Members
    getClubMembers: (clubId) => request(`clubs/${clubId}/members`, { method: 'GET', body: undefined }),
    joinClub: (clubId) => request(`clubs/${clubId}/members`, { method: 'POST', body: undefined, auth: true }),
    leaveClub: (clubId) => request(`clubs/${clubId}/members/me`, { method: 'DELETE', body: undefined, auth: true }),
    updateMemberRole: (clubId, userId, role) => request(`clubs/${clubId}/members/${userId}`, { method: 'PATCH', body: { role }, auth: true }),
    removeMember: (clubId, userId) => request(`clubs/${clubId}/members/${userId}`, { method: 'DELETE', body: undefined, auth: true })

}


import { createContext, useState, useContext, useEffect } from 'react';
import { api } from "../api"

/**
 * When creating a provider, there are 3 phases
 *  1.) Create the context
 *  2.) Create a provider.
 *          The (value) parameter of <context.Provider/> is what determines everything that
 *          is contained within the context
 *  3.) Create a way to retrieve the values withing the context
 */

// Creating the variable that holds the context
const AuthContext = createContext(null)

// The Provider itself
export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(true);


    useEffect(() => {
        if (!localStorage.getItem("access_token")) {
            setLoading(false);
            return;
        }
        api.me()
            .then(setUser)
            .catch((err) => {
                setUser(null);
                setError(err.message)
            })
            .finally(() => setLoading(false));  // Runs unconditionally whether or not the promise is resolved
    }, []);

    function logout() {
        localStorage.removeItem("access_token")
        setUser(null)
        setError("")
    }

    async function login(username, password) {
        try {
            const data = await api.login(username, password)
            localStorage.setItem("access_token", data.access_token)
            setUser(await api.me())
            setError("")
            return true
        } catch (err) {
            logout()
            setError(err.message)
            return false
        }
    }

    async function register(username, password, description) {
        try {
            await api.register(username, password, description)      // If there is a failure, it can only happen here
        } catch (err) {
            setError(err.message)
            return false
        }
        return login(username, password)
    }

    // Here are the things we want available within our context
    const values = { user, register, login, logout, error, loading }
    return (
        <AuthContext.Provider value={values}>
            {children}
        </AuthContext.Provider>
    );
}

// Retrieving the context
export function useAuth() {
    const ctx = useContext(AuthContext)
    if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
    return ctx;
}
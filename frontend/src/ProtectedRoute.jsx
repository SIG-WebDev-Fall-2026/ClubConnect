import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "./Providers/AuthProvider.jsx";

export default function ProtectedRoute() {
    const { user, loading } = useAuth();

    if (loading) return <h1>Loading... </h1>;
    if (!user) return <Navigate to="/log-in" replace/>

    return <Outlet />
}


import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "./Providers/AuthProvider.jsx";

export default function UnauthenticatedRoute() {
    const { user, loading } = useAuth();

    if (loading) return <h1>Loading... </h1>;
    if (user) return <Navigate to="/" replace/>

    return <Outlet />
}
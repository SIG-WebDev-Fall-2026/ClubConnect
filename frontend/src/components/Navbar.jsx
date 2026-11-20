import "../styles/Navbar.css"

export default function Navbar() {

    return (
        <nav className="navbar">
            <div className="navbar-content">
                <div className="navbar-logo">
                    <h1>ClubConnect</h1>
                </div>

                <div className="navbar-links">
                    <a href="/">Home</a>
                    <a href="/clubs">My Clubs</a>
                    <a href="/explore">Explore</a>
                </div>

                <div className="profile-menu">
                    <div className="profile-avatar"></div>
                    <span>John Doe</span>
                    <span>⏷</span>  {/* Placeholder for dropdown menu, fix later*/}
                </div> 
            </div>
        </nav>
    )
}
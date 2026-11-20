import { useState } from "react";
import "../styles/MyClubs.css";
import { Link } from "react-router-dom";

//dummy club data for till we connect to the backend

const dummyClubs = [
  {
    id: 1,
    name: "ACM Web Dev",
    description: "Learn web development, build projects, and collaborate with other students",
    role: "Member",
    icon: "💻",
  },
  {
    id: 2,
    name: "Computer Club",
    description: "Connect with students interested in programming, technology, and computing",
    role: "Member",
    icon: "🖥️",
  },
  {
    id: 3,
    name: "Honors Society",
    description: "Explore academic opportunities, leadership, and community involvement",
    role: "Member",
    icon: "🎓",
  },
{
    id: 4,
    name: "Honors Society 2",
    description: "Explore academic opportunities, leadership, and community involvement",
    role: "Member",
    icon: "🎓",
  },
];

export default function MyClubs() { 

    //Store the user's current search input
    const [search, setSearch] = useState("");

    //Filter clubs based on names
    const filteredClubs = dummyClubs.filter((club) => 
      club.name.toLowerCase().includes(search.toLowerCase())
    );

    return ( 
        <main className="myclubs">
            {/* Page heading */}
            <header className="myclubs-header">
                <h1>My Clubs</h1>
                <p>Here's a list of clubs you're currently a member of:</p>
            </header>

            {/* Main club list container */}
            <section className="myclubs-container">
                {/* search input */}
                <input 
                    className="myclubs-search"
                    type="text"
                    placeholder="Search your clubs..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                />

                {/* display matching clubs */}
                <div className="myclubs-list">
                    {filteredClubs.length > 0 ? (
                        filteredClubs.map((club) => (
                        <article className="myclubs-item" key={club.id}>
                            <div className="myclubs-icon">{club.icon}</div>

                            <div className="myclubs-info">
                                <div className="myclubs-name-row">
                                    <h2>{club.name}</h2>
                                    <span className="myclubs-role">{club.role}</span>
                                </div>

                                <p>{club.description}</p>
                            </div> 
                            {/* Arrow linking to the club's individual page */}
                            <Link
                            to={`/clubs/${club.id}`}
                            className="myclubs-arrow"
                            aria-label={`View ${club.name}`}
                            >
                            <span aria-hidden="true">›</span>
                            </Link>
                        </article>
                        ))
                    ) : (
                        <p className="myclubs-empty">No matching clubs found</p>
                    )}
                </div>
            </section>
        </main>
    );
}
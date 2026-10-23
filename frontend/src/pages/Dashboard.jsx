export default function Dashboard() {

    //Dummy Data for upcoming events and user clubs
    const upcomingEvents = [
    {
        id: 1,
        club: "ACM Web Dev",
        title: "General Body Meeting",
        date: "Oct 16",
        time: "1:00 PM",
        location: "CDRLC 2433",
    },
    {
        id: 2,
        club: "Halloween Club",
        title: "Spooky Git Workshop",
        date: "Oct 18",
        time: "6:00 PM",
        location: "SCE 302",
    },]

  const userClubs = [
    {
        id: 1,
        name: "ACM",
    },
    {
        id: 2,
        name: "Computer Club",
    },
    {
        id: 3,
        name: "Honors Society",
    },
  ]

    return (
        <main className="dashboard">
            <section className="dashboard-header">
                <h1>Welcome back, John Doe!👋</h1>
                <p> Here's what's happening with your clubs this week:</p>
            </section>

            <section className="dashboard-grid">
                <div className="dashboard-card upcoming-card">
                    <div className="section-header">
                        <h2>Upcoming</h2>
                    </div>

                    <div className="event-list">
                    {upcomingEvents.map((event) => (
                        <div className="event-item" key={event.id}>
                        
                        <div className="event-date">
                            <span>{event.date}</span>
                            <strong>{event.time}</strong>
                        </div>

                        <div className="event-info">
                            <h3>{event.title}</h3>
                            <p>{event.club}</p>
                        </div>

                        <div className="event-location">
                            <span>{event.location}</span>
                        </div>
                        </div>
                    ))}
                    </div>

                </div>

                <div className="dashboard-card clubs-card">
                    <div className="section-header">
                        <h2>Your Clubs</h2>
                    </div>
                    <div className="clubs-list">
                        {userClubs.map((club) => (
                            <div key={club.id} className="club-item">
                                <div className="club-icon">
                                    <span role="img" aria-label="club">🏛️</span> 
                                </div>
                                <span>{club.name}</span>
                            </div>
                        ))}
                    </div>

                    <button className="manage-button">Manage Clubs →</button>
                </div>
            </section>

            <section className="explore-section">
                <h2>Explore</h2>
                <p> UIC Clubs, recommended for you:</p>

                <div className="explore-grid">
                    <div className="explore-card"></div>
                    <div className="explore-card"></div>
                    <div className="explore-card"></div>
                </div>
            </section>
        </main>
    )
}
import "../styles/LogIn.css";

import {useAuth} from "../Providers/AuthProvider.jsx"

export default function Register() {
  const {register, error} = useAuth()

  async function handleSubmit(e){
    e.preventDefault();

    const formData = new FormData(e.target);
    const username = formData.get("username")
    const password = formData.get("password")
    try {
        await register(username, password)
    } catch (err) {
        console.log(err);
    }
  }
  return (
    <>
      <div className="login-screen">
        <header className="screen-header">
          <h1 className="site-title">Club Connect</h1>
        </header>
        <main className="center-container">
          <div className="auth-box">
            <div className="title-badge"> <h2>Register</h2> </div>
            { error ? <p>{error}</p> : <></> }
            <form onSubmit={handleSubmit}>
              <div className="authenticate">
                <div className="input-group">
                  <span className="material-symbols-rounded input-icon">person</span>
                  <input 
                    type = "text"
                    name="username"
                    placeholder = "Username" 
                    className = "field-input" 
                    required
                  />
                </div>

                <div className="input-group">
                  <span className="material-symbols-rounded input-icon">lock</span>
                  <input 
                    type="password"
                    name="password"
                    placeholder="Password" 
                    className="field-input"
                    required
                  />
                </div>

                <div className="action-buttons">
                  <button type="submit" className="action-btn"> Register </button>
                </div>
              </div>
            </form>
          </div>
        </main>
      </div>
    </>
  );
}
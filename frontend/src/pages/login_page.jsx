import "../styles/login_page.css";

export default function LoginPage() {
  return (
    <div className="login-screen">
      <header className="screen-header">
        <h1 className="site-title">SITE LOGO</h1>
      </header>

      <main className="center-container">
        <div className="auth-box">
          
          <div className="title-badge"> <h2>Welcome to SITE NAME</h2> </div>

          <div className="authenticate">
            <div className="input-group">
              <span className="material-symbols-rounded input-icon">person</span>
              <input type="text" placeholder="Email" className="field-input" />
            </div>

            <div className="input-group">
              <span className="material-symbols-rounded input-icon">lock</span>
              <input type="password" placeholder="Password" className="field-input"/>
            </div>

            <div className="action-buttons">
              <button type="button" className="action-btn"> Sign In </button>
              <button type="button" className="action-btn create-btn"> Create an Account</button>
            </div>
            
          </div>
        </div>
      </main>
    </div>
  );
}
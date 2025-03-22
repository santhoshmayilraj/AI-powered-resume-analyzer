import { Link, useLocation } from "react-router-dom";
import "./Navbar.css";

function Navbar() {
  const location = useLocation();
  
  // Function to check if the link is active
  const isActive = (path) => {
    return location.pathname === path ? "active" : "";
  };

  return (
    <nav className="navbar">
      <div className="container navbar-container">
        <Link to="/" className="navbar-logo">
          ResumeMatch
        </Link>
        
        <div className="navbar-links">
          <Link to="/" className={`nav-link ${isActive("/")}`}>
            Home
          </Link>
          <Link to="/about" className={`nav-link ${isActive("/about")}`}>
            About
          </Link>
          <Link to="/upload" className={`nav-link ${isActive("/upload")}`}>
            Upload Resume
          </Link>
        </div>
        
        <div className="navbar-auth">
          <Link to="/login" className={`nav-link ${isActive("/login")}`}>
            Login
          </Link>
          <Link to="/signup" className="btn btn-primary">
            Sign Up
          </Link>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
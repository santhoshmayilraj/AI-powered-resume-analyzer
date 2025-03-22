import { useState } from "react";
import { Link } from "react-router-dom";
import "./Login.css";

function Login() {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    rememberMe: false
  });
  
  const [formErrors, setFormErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState({ text: "", type: "" });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === "checkbox" ? checked : value
    });
    
    // Clear error when field is updated
    if (formErrors[name]) {
      setFormErrors({
        ...formErrors,
        [name]: ""
      });
    }
  };

  const validateForm = () => {
    const errors = {};
    
    if (!formData.email.trim()) {
      errors.email = "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = "Email is invalid";
    }
    
    if (!formData.password) {
      errors.password = "Password is required";
    }
    
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setIsLoading(true);
    setMessage({ text: "", type: "" });
    
    // Simulate API call
    try {
      // Replace with actual API call
      setTimeout(() => {
        setMessage({
          text: "Login successful!",
          type: "success"
        });
        setIsLoading(false);
        // Here you would normally redirect the user or update app state
      }, 1500);
    } catch (error) {
      setMessage({
        text: "Invalid email or password. Please try again.",
        type: "error"
      });
      setIsLoading(false);
    }
  };

  return (
    <div className="page auth-page">
      <div className="container">
        <div className="form-container auth-form-container">
          <h1>Welcome Back</h1>
          <p className="auth-subtitle">Sign in to your ResumeMatch account</p>
          
          {message.text && (
            <div className={`alert ${message.type === "success" ? "alert-success" : "alert-error"}`}>
              {message.text}
            </div>
          )}
          
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="email">Email Address</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className={formErrors.email ? "input-error" : ""}
              />
              {formErrors.email && <p className="error-message">{formErrors.email}</p>}
            </div>
            
            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                className={formErrors.password ? "input-error" : ""}
              />
              {formErrors.password && <p className="error-message">{formErrors.password}</p>}
            </div>
            
            <div className="form-group remember-forgot">
              <div className="checkbox-group">
                <input
                  type="checkbox"
                  id="rememberMe"
                  name="rememberMe"
                  checked={formData.rememberMe}
                  onChange={handleChange}
                />
                <label htmlFor="rememberMe" className="checkbox-label">Remember me</label>
              </div>
              <Link to="/forgot-password" className="forgot-link">Forgot password?</Link>
            </div>
            
            <button 
              type="submit" 
              className={`btn btn-block ${isLoading ? "btn-loading" : ""}`}
              disabled={isLoading}
            >
              {isLoading ? "Signing in..." : "Sign In"}
            </button>
          </form>
          
          <div className="auth-footer">
            <p>
              Don't have an account? <Link to="/signup" className="auth-link">Sign up</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;
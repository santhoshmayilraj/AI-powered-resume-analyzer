import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getAuthToken } from "../utils/auth";
import "./UploadResume.css";

function UploadResume() {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [message, setMessage] = useState({
    text: "",
    type: ""
  });
  const [isLoading, setIsLoading] = useState(false);

  // Check authentication on component mount
  useEffect(() => {
    const token = getAuthToken();
    if (!token) {
      navigate("/login", { state: { from: "/upload", message: "Please login to access this page" } });
    }
  }, [navigate]);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
    setMessage({ text: "", type: "" });
  };

  const handleJobChange = (event) => {
    setJobDescription(event.target.value);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!file || !jobDescription) {
      setMessage({
        text: "Please select a file and enter a job description.",
        type: "error"
      });
      return;
    }

    setIsLoading(true);
    
    try {
      const token = getAuthToken();
      
      if (!token) {
        navigate("/login", { state: { from: "/upload", message: "Session expired. Please login again." } });
        return;
      }
      
      const formData = new FormData();
      formData.append('file', file);
      formData.append('job_description', jobDescription);
      
      // Actual API call with authentication
      const response = await fetch("http://127.0.0.1:8000/api/upload-resume/", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`
        },
        body: formData
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        
        // Handle authentication errors
        if (response.status === 401) {
          navigate("/login", { state: { from: "/upload", message: "Session expired. Please login again." } });
          return;
        }
        
        throw new Error(errorData.error || "Error uploading resume");
      }
      
      // Remove the unused data variable and directly set success message
      setMessage({
        text: "Resume uploaded and analyzed successfully!",
        type: "success"
      });
      
    } catch (error) {
      console.error("Upload error:", error);
      setMessage({
        text: error.message || "Error uploading file. Please try again.",
        type: "error"
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="page upload-page">
      <div className="container">
        <div className="upload-header">
          <h1>Resume Analyzer</h1>
          <p>Upload your resume and job description to see how well they match</p>
        </div>
        
        <div className="form-container upload-form-container">
          {message.text && (
            <div className={`alert ${message.type === "success" ? "alert-success" : "alert-error"}`}>
              {message.text}
            </div>
          )}
          
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="resume">Upload Resume</label>
              <div className="file-input-wrapper">
                <input 
                  type="file" 
                  id="resume" 
                  onChange={handleFileChange} 
                  accept=".pdf,.doc,.docx"
                />
                <div className="file-name">
                  {file ? file.name : "No file selected"}
                </div>
              </div>
            </div>
            
            <div className="form-group">
              <label htmlFor="job-description">Job Description</label>
              <textarea
                id="job-description"
                placeholder="Paste the job description here..."
                value={jobDescription}
                onChange={handleJobChange}
                rows="6"
              ></textarea>
            </div>
            
            <button 
              type="submit" 
              className={`btn btn-block ${isLoading ? "btn-loading" : ""}`}
              disabled={isLoading}
            >
              {isLoading ? "Analyzing..." : "Analyze Resume"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default UploadResume;
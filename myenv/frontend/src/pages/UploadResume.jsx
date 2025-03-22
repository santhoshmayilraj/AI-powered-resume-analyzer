import { useState } from "react";
import "./UploadResume.css";

function UploadResume() {
  const [file, setFile] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [message, setMessage] = useState({
    text: "",
    type: ""
  });
  const [isLoading, setIsLoading] = useState(false);

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
    
    // Simulate API call
    try {
      // Replace with your actual API call
      setTimeout(() => {
        setMessage({
          text: "Resume uploaded and analyzed successfully!",
          type: "success"
        });
        setIsLoading(false);
      }, 2000);
      
    } catch (error) {
      console.error("Upload error:", error);
      setMessage({
        text: "Error uploading file. Please try again.",
        type: "error"
      });
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
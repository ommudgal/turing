import React from 'react';
import { useNavigate } from 'react-router-dom';

const Success = ({ useremail }) => {
  const navigate = useNavigate();

  const handleBackToHome = () => {
    navigate('/');
  };

  return (
    <div className="success-container">
      <div className="success-content">
        <div className="success-icon">
          <svg
            width="80"
            height="80"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#4CAF50"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
            <polyline points="22,4 12,14.01 9,11.01"></polyline>
          </svg>
        </div>
        
        <h2 className="success-title">Registration Successful! 🎉</h2>
        
        <div className="success-message">
          <p>Congratulations! Your registration for <strong>The Turing Test 25</strong> has been completed successfully.</p>
          {useremail && (
            <p>Your email <strong>{useremail}</strong> has been verified.</p>
          )}
        </div>

        <div className="success-details">
          <div className="detail-item">
            <span className="detail-icon">📧</span>
            <span>Email verification completed</span>
          </div>
          <div className="detail-item">
            <span className="detail-icon">✅</span>
            <span>Registration confirmed</span>
          </div>
          <div className="detail-item">
            <span className="detail-icon">📅</span>
            <span>Event details will be shared soon</span>
          </div>
        </div>

        <div className="success-actions">
          <button 
            className="btn-primary"
            onClick={handleBackToHome}
          >
            Back to Home
          </button>
        </div>

        <div className="success-footer">
          <p>Thank you for registering for The Turing Test 25!</p>
          <p>We look forward to seeing you at the event.</p>
        </div>
      </div>
    </div>
  );
};

export default Success;

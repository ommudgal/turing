
import axios from 'axios';
import React, { useState } from 'react';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5054/api/v1';

const Verification = ({useremail}) => {
  const [otp, setOtp] = useState(Array(5).fill("")); // Changed from 4 to 5 for new format
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (value, index) => {
    if (/^[A-Za-z0-9]?$/.test(value)) { 
        const newOtp = [...otp];
        newOtp[index] = value.toUpperCase(); // Force uppercase for consistency
        setOtp(newOtp);

        // Auto-focus next input
        if (value && index < 4) { // Changed from 3 to 4 for 5-character OTP
          document.getElementById(`otp-input-${index + 1}`).focus();
        }
    }
  };

  const handleSubmit = async () => {
    if (isSubmitting) {
      return; // Prevent multiple submissions
    }

    const enteredOtp = otp.join("");
    
    if (enteredOtp.length !== 5) {
      toast.error("Please enter the complete 5-character verification code.");
      return;
    }

    setIsSubmitting(true);
    
    try {
      console.log("Sending body:", { otp: enteredOtp, email: useremail });
      const response = await axios.post(
        `${API_URL}/student/verify`,
        { otp: enteredOtp, email: useremail },
        {
          withCredentials: true,
          headers: { "Content-Type": "application/json" }
        }
      );
      console.log("Response:", response.data);
      
      if (response.data.success) {
        toast.success("🎉 Email verified successfully! Registration completed.");
        setOtp(new Array(5).fill("")); // Clear 5-character OTP
        // You might want to redirect to a success page here
        // navigate("/success");
      }
    } catch (error) {
      console.error("Error Response:", error.response?.data || error.message);
      
      if (error.response?.status === 400) {
        toast.error("Invalid or expired verification code. Please try again.");
      } else {
        toast.error("Verification failed. Please try again.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };
    

  const handleResend = async() => {
    try {
      const response = await axios.get(`${API_URL}/student/resend-otp?email=${useremail}`, {withCredentials:true});
      console.log("Resend response:", response);
      
      if (response.data.success) {
        toast.success("New verification code sent to your email!", {
          position: "top-right",
          autoClose: 3000,
          hideProgressBar: true,
        });
        setOtp(new Array(5).fill("")); // Clear current OTP inputs
      }
    } catch (error) {
      console.error("Resend error:", error.response?.data || error.message);
      toast.error("Failed to resend verification code. Please try again.", {
        position: "top-right",
        autoClose: 3000,
        hideProgressBar: true,
      });
    }
  };

  return (
    <div className="verification">
      <ToastContainer />
      <div className="verihead">Verification Code</div>
      <div className="para">
        We have sent a 5-character verification code to your college id <span>{useremail}</span> ✏
      </div>
      <div className="otp">
        {otp.map((digit, index) => (
          <input
            key={index}
            id={`otp-input-${index}`}
            type="text"
            className="no"
            maxLength="1"
            value={digit}
            onChange={(e) => handleChange(e.target.value, index)}
            onFocus={(e) => e.target.select()}
          />
        ))}
      </div>
      
        <button 
          className="submitbtn" 
          onClick={handleSubmit}
          disabled={isSubmitting || otp.some(digit => digit === "")}
        >
          {isSubmitting ? "Verifying..." : "Submit"}
        </button>
     
      <div className="resend" onClick={handleResend}>
        Resend OTP
      </div>
    </div>
  );
};

export default Verification;

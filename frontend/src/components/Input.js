
import axios from 'axios';
import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import ReCAPTCHA from 'react-google-recaptcha';

const API_URL = process.env.REACT_APP_API_URL || 'http://mlcoe.live/api/v1';

const Input = ({handleevent}) => {
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [branch, setBranch] = useState('');
  const [univRoll, setUnivRoll] = useState('');
  const [gender, setGender] = useState('');
  const [scholarType, setScholarType] = useState('');
  const [studentNumber, setStudentNumber] = useState('');
  const [email, setEmail] = useState('');
  const [mobile, setMobile] = useState('');
  const [domain, setDomain] = useState("");
  const [recaptchaToken, setRecaptchaToken] = useState('');
  const recaptchaRef = useRef();
    
// Invisible reCAPTCHA enabled
  const regexPatterns = {
    name: /^[A-Za-z\s]{3,30}$/,
    branch: /^[A-Za-z\s()]+$/,
    mobile: /^[0-9]{10}$/,
    studentNumber: /^24[0-9]{5,18}$/,
    email: /^[a-zA-Z0-9._%+-]+@akgec\.ac\.in$/,
  };

  const validateField = (field, value) => {
    const pattern = regexPatterns[field];

    // Early validation for student number - show error immediately if not starting with 24
    if (field === "studentNumber") {
      if (value.length >= 1 && !value.startsWith("2")) {
        setErrors((prev) => ({ ...prev, studentNumber: "Student number must start with 24" }));
        return;
      }
      if (value.length >= 2 && !value.startsWith("24")) {
        setErrors((prev) => ({ ...prev, studentNumber: "Student number must start with 24" }));
        return;
      }
      if (value.length >= 7 && value.length <= 20 && value.startsWith("24")) {
        // Valid format so far, clear error
        setErrors((prev) => {
          const { studentNumber: _, ...rest } = prev;
          return rest;
        });
      } else if (value.length > 20) {
        setErrors((prev) => ({ ...prev, studentNumber: "Student number cannot exceed 20 characters" }));
        return;
      } else if (value.length > 0 && value.length < 7 && value.startsWith("24")) {
        setErrors((prev) => ({ ...prev, studentNumber: "Student number must be at least 7 characters" }));
        return;
      }
    }

    // Basic pattern validation for complete input
    if (pattern && value.length > 0 && !pattern.test(value)) {
      if (field === "studentNumber") {
        setErrors((prev) => ({ ...prev, [field]: "Student number must start with 24" }));
      } else if (field === "email") {
        setErrors((prev) => ({ ...prev, [field]: "Email must belong to akgec.ac.in domain" }));
      } else {
        setErrors((prev) => ({ ...prev, [field]: `Invalid ${field}` }));
      }
      return;
    }

    // Additional validation for email - must contain student number
    if (field === "email" && studentNumber && value.length > 0) {
      if (!value.endsWith("@akgec.ac.in") && value.includes("@")) {
        setErrors((prev) => ({ ...prev, email: "Email must belong to akgec.ac.in domain" }));
        return;
      }
      if (value.endsWith("@akgec.ac.in") && !value.includes(studentNumber)) {
        setErrors((prev) => ({ ...prev, email: `Email must contain student number ${studentNumber}` }));
        return;
      }
    }

    // Cross-field validation when student number changes
    if (field === "studentNumber" && email) {
      if (!email.includes(value)) {
        setErrors((prev) => ({ ...prev, email: `Email must contain student number ${value}` }));
      } else {
        // Clear email error if it now matches
        setErrors((prev) => {
          const { email: _, ...rest } = prev;
          return rest;
        });
      }
    }

    // Clear current field error if validation passes
    if (value.length === 0 || (pattern && pattern.test(value))) {
      setErrors((prev) => {
        const { [field]: _, ...rest } = prev;
        return rest;
      });
    }
  };


  const handleClick = async(e) => {
    e.preventDefault();
    
    if (isSubmitting) {
      return; // Prevent multiple submissions
    }

    // Validate all required fields
    if (
      !name || !branch || !univRoll || !gender || !scholarType ||
      !studentNumber || !email || !mobile || !domain
    ) {
      toast.error("Please fill all the required fields.");
      return;
    }

    // Validate email and student number match
    if (!email.includes(studentNumber)) {
      toast.error("Student number must match the number in email ID.");
      return;
    }

    // Check for validation errors
    if (Object.keys(errors).length > 0) {
      toast.error("Please fix the validation errors before submitting.");
      return;
    }

    // Execute invisible reCAPTCHA
    if (recaptchaRef.current) {
      try {
        const token = await recaptchaRef.current.executeAsync();
        if (!token) {
          toast.error("reCAPTCHA verification failed. Please try again.");
          return;
        }
        setRecaptchaToken(token);
        
        // Validate reCAPTCHA with backend
        const captchaResponse = await axios.post(`${API_URL}/student/validate`, {
          recaptchaValue: token
        });
        
        if (!captchaResponse.data.success) {
          toast.error("Security verification failed. Please try again.");
          recaptchaRef.current.reset();
          return;
        }
      } catch (captchaError) {
        console.error("reCAPTCHA error:", captchaError);
        toast.error("Security verification failed. Please try again.");
        if (recaptchaRef.current) {
          recaptchaRef.current.reset();
        }
        return;
      }
    } else {
      toast.error("Security verification not loaded. Please refresh and try again.");
      return;
    }

    setIsSubmitting(true);
    
    try {
      handleevent(email);

      const formData = {
        fullName: name,
        branch: branch,
        rollNumber: univRoll,
        gender: gender,
        scholar: scholarType,
        studentNumber: studentNumber,
        studentEmail: email,
        mobileNumber: mobile,
        domain: domain
      };

      console.log("Form data:", formData);
      
      const response = await axios.post(`${API_URL}/student/register`,
        formData,
        { withCredentials: true } 
      );
      
      console.log("Response:", response.data);
      
      if (response.data.success) {
        toast.success("Registration successful! Please check your email for verification code. 🎉");
        navigate("/Verify");
        
        // Clear form
        setName('');
        setBranch('');
        setUnivRoll('');
        setGender('');
        setScholarType('');
        setStudentNumber('');
        setEmail('');
        setMobile('');
        setDomain('');
        setRecaptchaToken('');
        // Reset reCAPTCHA for next use
        if (recaptchaRef.current) {
          recaptchaRef.current.reset();
        }
      }
    } catch (error) {
      console.error("Registration error:", error.response?.data || error.message);
      
      if (error.response?.status === 400) {
        toast.error(error.response.data.detail || "Registration failed. Please check your details.");
      } else if (error.response?.status === 500) {
        toast.error("Server error. Please try again later.");
      } else {
        toast.error("Registration failed. Please try again.");
      }
    } finally {
      setIsSubmitting(false);
      // Reset reCAPTCHA on error
      if (recaptchaRef.current) {
        recaptchaRef.current.reset();
      }
    }
  };

  return (
    <div className="inputcontainer">
      <form>
        <div className="name">
          <label htmlFor="name">Name</label>
          <input
            type="text"
            id="name"
            name="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            onBlur={(e) => validateField("name", e.target.value)}
            required
          />
          {errors.name && <small className="error">{errors.name}</small>}
        </div>

        <div className="input">
          <label htmlFor="branch">Branch</label>
          <select
            type="text"
            id="branch"
            name="branch"
            value={branch}
            onChange={(e) => setBranch(e.target.value)}
            onBlur={(e) => validateField("branch", e.target.value)}
            required
          >
             <option value="" disabled>Select Branch</option>
              <option value="CSIT">CSIT</option>
              <option value="CSE">CSE</option>
              <option value="CSE(AIML)">CSE(AIML)</option>
               <option value="CSE(DS)">CSE(DS)</option>
                <option value="CSE(HINDI)">CSE(HINDI)</option>
                 <option value="IT">IT</option>
                  <option value="EN">EN</option>
                   <option value="CIVIL">CIVIL</option>
                    <option value="MECHANICAL">MECHANICAL</option>
                    <option value="AIML">AIML</option>
                       <option value="ECE">ECE</option>
                    <option value="CS">CS</option>
                    
            </select>


          {errors.branch && <small className="error">{errors.branch}</small>}
        </div>
        <div className="input">
          <label htmlFor="domain">Domain</label>
          <select
            type="text"
            id="domain"
            name="domain"
            value={domain}
            onChange={(e) => setDomain(e.target.value)}
            onBlur={(e) => validateField("domain", e.target.value)}
            required
          >
             <option value="" disabled>Select Domain</option>
              <option value="Machine Learning">Machine Learning</option>
              <option value="Web Developer">Web Developer</option>
              <option value="Designer">Designer</option>
            </select>


          {errors.domain && <small className="error">{errors.domain}</small>}
        </div>

        <div className="input">
          <label htmlFor="univRoll">University Roll no.</label>
          <input
            type="text"
            id="univRoll"
            name="univRoll"
            value={univRoll}
            onChange={(e) => setUnivRoll(e.target.value)}
            required
          />
        </div>

        <div className="input1">
          <div className="gender">
            <label htmlFor="gender">Gender</label>
            <select
              id="gender"
              name="gender"
              value={gender}
              onChange={(e) => setGender(e.target.value)}
              required
            >
              <option value="" disabled>Select Gender</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div className="scholar">
            <label htmlFor="scholar-type">Scholar</label>
            <select
              name="scholarType"
              value={scholarType}
              onChange={(e) => setScholarType(e.target.value)}
              required
            >
              <option value="" disabled>Select Scholar Type</option>
              <option value="day">Day Scholar</option>
              <option value="hostel">Hosteller</option>
            </select>
          </div>
        </div>

        <div className="input">
          <label htmlFor="student-number">Student Number</label>
          <input
            type="tel"
            name="studentNumber"
            value={studentNumber}
            onChange={(e) => {
              setStudentNumber(e.target.value);
              validateField("studentNumber", e.target.value);
            }}
            onBlur={(e) => validateField("studentNumber", e.target.value)}
            required
          />
          {errors.studentNumber && (
            <small className="error">{errors.studentNumber}</small>
          )}
        </div>

        <div className="input">
          <label htmlFor="email">College Email Id</label>
          <input
            type="email"
            name="email"
            value={email}
            onChange={(e) => {
              setEmail(e.target.value);
              validateField("email", e.target.value);
            }}
            onBlur={(e) => validateField("email", e.target.value)}
            required
          />
          {errors.email && <small className="error">{errors.email}</small>}
        </div>

        <div className="input">
          <label htmlFor="mobile">Mobile No</label>
          <input
            type="tel"
            name="mobile"
            value={mobile}
            onChange={(e) => setMobile(e.target.value)}
            onBlur={(e) => validateField("mobile", e.target.value)}
            required
          />
          {errors.mobile && <small className="error">{errors.mobile}</small>}
        </div>

        {/* Invisible reCAPTCHA */}
        <ReCAPTCHA
          ref={recaptchaRef}
          size="invisible"
          sitekey={process.env.REACT_APP_RECAPTCHA_SITE_KEY || "6LfGaa8rAAAAAC7YlsrcYzwAYPZKO0nny7TFQn65"}
          onChange={(token) => setRecaptchaToken(token)}
        />
        
        {/* reCAPTCHA Privacy Notice */}
        <div style={{
          fontSize: '12px',
          color: '#999',
          textAlign: 'center',
          margin: '10px 0',
          lineHeight: '1.4'
        }}>
          This site is protected by reCAPTCHA and the Google{' '}
          <a 
            href="https://policies.google.com/privacy" 
            target="_blank" 
            rel="noopener noreferrer"
            style={{ color: '#9E4084', textDecoration: 'underline' }}
          >
            Privacy Policy
          </a>
          {' '}and{' '}
          <a 
            href="https://policies.google.com/terms" 
            target="_blank" 
            rel="noopener noreferrer"
            style={{ color: '#9E4084', textDecoration: 'underline' }}
          >
            Terms of Service
          </a>
          {' '}apply.
        </div>
       
        <button
          onClick={handleClick}
          type="submit"
          className="verifybtn input"
          disabled={isSubmitting}
        >
          {isSubmitting ? "Submitting..." : "Verify"}
        </button>
      </form>
      
    </div>
  );
}

export default Input;


import axios from 'axios';
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import ReCAPTCHA from 'react-google-recaptcha';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5054/api/v1';

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
  const [captchaSize, setCaptchaSize] = useState('normal');
  const [domain, setDomain] = useState("");
  const [captchaToken, setCaptchaToken] = useState('');
  const [captchaVerified, setCaptchaVerified] = useState(false);
    
const handleCaptcha = async(token) => {
    console.log("Captcha token:", token);
    setCaptchaToken(token);
    
    if (!token) {
      setCaptchaVerified(false);
      return;
    }
    
    try {
      const res = await axios.post(`${API_URL}/student/validate`, {recaptchaValue:token},{withCredentials:true});
      console.log("Captcha verified:", res);
      setCaptchaVerified(true);
      toast.success("Captcha verified successfully!");
    } catch (err) {
      console.error("Captcha verification failed:", err.response?.data || err.message);
      setCaptchaVerified(false);
      toast.error("Captcha verification failed. Please try again.");
    }
  };
  const regexPatterns = {
    name: /^[A-Za-z\s]{3,30}$/, 
    branch: /^[A-Za-z\s]+$/,
    email: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
    mobile: /^[0-9]{10}$/, 
    studentNumber: /^[0-9]{5,7}$/,
  };

 const validateField = (field, value) => {
  const pattern = regexPatterns[field];
  if (pattern && !pattern.test(value)) {
    setErrors((prev) => ({ ...prev, [field]: `Invalid ${field}` }));
    return;
  }


  if (field === "studentNumber" && !(value.startsWith("23") || value.startsWith("24"))) {
    setErrors((prev) => ({ ...prev, studentNumber: "Student number must start with 23 or 24" }));
    return;
  }

 
  setErrors((prev) => {
    const { [field]: _, ...rest } = prev;
    return rest;
  });

  
  if ((field === "email" || field === "studentNumber") && email && studentNumber) {
    const emailMatch = email.match(/\d+/g); 
    const numberInEmail = emailMatch ? emailMatch.join('') : '';
    if (!email.includes(studentNumber) || !numberInEmail.includes(studentNumber)) {
      setErrors((prev) => ({
        ...prev,
        email: "Student number does not match with email ID",
      }));
    } else {
      setErrors((prev) => {
        const { email: _, ...rest } = prev;
        return rest;
      });
    }
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

    // Check captcha verification
    if (!captchaVerified) {
      toast.error("Please complete the captcha verification.");
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
        setCaptchaToken('');
        setCaptchaVerified(false);
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
            onChange={(e) => setStudentNumber(e.target.value)}
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
            onChange={(e) => setEmail(e.target.value)}
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
        <div className="handleCaptcha">
<ReCAPTCHA
        sitekey="6LfZSKgrAAAAAC4TqAYwouSIUC1ACsattTPVy22f"
        onChange={handleCaptcha}
        size={captchaSize}
      />
      </div>
       
        <button
          onClick={handleClick}
          type="submit"
          className="verifybtn input"
          disabled={isSubmitting || !captchaVerified}
        >
          {isSubmitting ? "Submitting..." : "Verify"}
        </button>
      </form>
    </div>
  );
};


export default Input;

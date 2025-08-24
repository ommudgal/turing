
import './App.css';
import Input from './components/Input';
import { BrowserRouter as Router,Route,Routes } from 'react-router';
import Verification from './components/Verification';
import Success from './components/Success';
import { ToastContainer } from 'react-toastify';
import { useState } from 'react';

function App() {
  const[useremail,setUserEmail]=useState();
  const handleevent=(email)=>{
    setUserEmail(email);
  }
  return (
    <Router>
    <div className="Main">
      <div className="logo">
        <img src="./new logo.png" alt="/" height="100%" width="100%"/>
        <div className="top-right">
          <img src="./top-right.png" alt=""  height="100%" width="100%"/>
        </div>
         <div className="bottom-right">
          <img src="./bottom-right.png" alt="" height="100%" width="100%" />
        </div>
        <div className="top-left">
          <img src="./top-left.png" alt="" height="100%" width="100%" />
        </div>
         <div className="top-left-ball">
          <img src="./top-left-ball.png" alt="" height="100%" width="100%" />
        </div>
        <div className="top-left-ball2">
          <img src="./top-left-ball2.png" alt="" height="100%" width="100%" />
        </div>
         <div className="bottom-left">
          <img src="./bottom-left.png" alt="" height="100%" width="100%" />
        </div>
         <div className="bottom-left-ball">
          <img src="./bottom-left-ball.png" alt="" height="100%" width="100%" />
        </div>
         <div className="bottom-left-ball2">
          <img src="./bottom-left-ball2.png" alt="" height="100%" width="100%" />
        </div>
      </div>
      <h1>The Turing Test 25</h1>
      <Routes>
      <Route path ="/" element={<Input  handleevent={handleevent}/>}/>
       <Route path ="/Verify" element={ <Verification useremail={useremail} />}/>
       <Route path ="/Success" element={ <Success useremail={useremail} />}/>
      </Routes>
       <ToastContainer position="top-right" autoClose={3000} />

      <div className="query">
        <div className="query-title">For any Query</div>
        <div className="query-contacts">
          <div className="query-contact">
            <span className="contact-name">Arpit Pandey</span>
            <span className="contact-number">9559983740</span>
          </div>
          <div className="query-contact">
            <span className="contact-name">Mohd Ziya</span>
            <span className="contact-number">6387120082</span>
          </div>
        </div>
      </div>
    </div>
    </Router>
  );
}

export default App;

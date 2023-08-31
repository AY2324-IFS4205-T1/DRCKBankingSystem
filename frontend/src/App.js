import React from 'react';
import './App.css';
import Navbar from './components/Navbar';
import { BrowserRouter as Router, Routes, Route }
    from 'react-router-dom';
import Home from './pages/index';
import Apply from './pages/apply';
import Atm from './pages/atm';
import Balance from './pages/balance';
import Login from './pages/login';
import Transfer from './pages/transfer';

function App() {
    return (
        <Router>
            <Navbar />
            <Routes>
                <Route exact path='/' exact element={<Home />} />
                <Route path='/apply' element={<Apply />} />
                <Route path='/atm' element={<Atm />} />
                <Route path='/balance' element={<Balance />} />
                <Route path='/login' element={<Login />} />
                <Route path='/transfer' element={<Transfer />} />
            </Routes>
        </Router>
    );
}

export default App;
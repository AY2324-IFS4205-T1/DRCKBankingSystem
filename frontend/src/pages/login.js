import React from 'react';
import axios from 'axios';
import { useState, useEffect } from 'react';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';

axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';
axios.defaults.withCredentials = true;

const client = axios.create({
    baseURL: "http://127.0.0.1:8000"
});

const Login = () => {
    const [currentUser, setCurrentUser] = useState();
    const [registrationToggle, setRegistrationToggle] = useState(false);
    const [email, setEmail] = useState('');
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    useEffect(() => {
        client.get("/user")
            .then(function (res) {
                setCurrentUser(true);
            })
            .catch(function (error) {
                setCurrentUser(false);
            });
    }, []);

    function update_form_btn() {
        if (registrationToggle) {
            document.getElementById("form_btn").innerHTML = "Register";
            setRegistrationToggle(false);
        } else {
            document.getElementById("form_btn").innerHTML = "Log in";
            setRegistrationToggle(true);
        }
    }

    function submitRegistration(e) {
        e.preventDefault();
        client.post(
            "/register",
            {
                email: email,
                username: username,
                password: password
            }
        ).then(function (res) {
            client.post(
                "/login",
                {
                    email: email,
                    password: password
                }
            ).then(function (res) {
                setCurrentUser(true);
            });
        });
    }

    function submitLogin(e) {
        e.preventDefault();
        client.post(
            "/login",
            {
                email: email,
                password: password
            }
        ).then(function (res) {
            setCurrentUser(true);
        });
    }

    function submitLogout(e) {
        e.preventDefault();
        client.post(
            "/logout",
            { withCredentials: true }
        ).then(function (res) {
            setCurrentUser(false);
        });
    }

    if (currentUser) {
        return (
            <div className="center">
                <h1>Authentication App</h1>
                <form onSubmit={e => submitLogout(e)}>
                    <Button type="submit" variant="light">Log out</Button>
                </form>
                <h2>You're logged in!</h2>
            </div>
        );
    }
    return (
        <div className="center">
            <h1>Authentication App</h1>
            <form onSubmit={e => submitLogout(e)}>
                <Button id="form_btn" onClick={update_form_btn} variant="light">Register</Button>
            </form>
            <h2>You're logged in!</h2>
            {registrationToggle ? (
                <div className="center">
                    <Form onSubmit={e => submitRegistration(e)}>
                        <Form.Group className="mb-3" controlId="formBasicEmail">
                            <Form.Label>Email address</Form.Label>
                            <Form.Control type="email" placeholder="Enter email" value={email} onChange={e => setEmail(e.target.value)} />
                            <Form.Text className="text-muted">
                                We'll never share your email with anyone else.
                            </Form.Text>
                        </Form.Group>
                        <Form.Group className="mb-3" controlId="formBasicUsername">
                            <Form.Label>Username</Form.Label>
                            <Form.Control type="text" placeholder="Enter username" value={username} onChange={e => setUsername(e.target.value)} />
                        </Form.Group>
                        <Form.Group className="mb-3" controlId="formBasicPassword">
                            <Form.Label>Password</Form.Label>
                            <Form.Control type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} />
                        </Form.Group>
                        <Button variant="primary" type="submit">
                            Submit
                        </Button>
                    </Form>
                </div>
            ) : (
                <div className="center">
                    <Form onSubmit={e => submitLogin(e)}>
                        <Form.Group className="mb-3" controlId="formBasicEmail">
                            <Form.Label>Email address</Form.Label>
                            <Form.Control type="email" placeholder="Enter email" value={email} onChange={e => setEmail(e.target.value)} />
                            <Form.Text className="text-muted">
                                We'll never share your email with anyone else.
                            </Form.Text>
                        </Form.Group>
                        <Form.Group className="mb-3" controlId="formBasicPassword">
                            <Form.Label>Password</Form.Label>
                            <Form.Control type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} />
                        </Form.Group>
                        <Button variant="primary" type="submit">
                            Submit
                        </Button>
                    </Form>
                </div>
            )}
        </div>
    );
};

export default Login;
import React, { useState } from 'react'
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from '@/components/ui/button';
import { useNavigate } from 'react-router-dom';

function Login({ onSwitchToSignup }) {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const navigate = useNavigate();
    const handleLogin = async (e) => {
        e.preventDefault();

        setError('');  // Clear any previous error

        try {
            // Send a POST request to the backend
            const response = await fetch('http://52.91.54.146:5000/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email,
                    password
                })
            });

            const data = await response.json();

            if (response.ok) {
                setSuccess(data.user_id);
                setError('');  // Clear error
                // setSuccessMessage("Sign in successful.");
                // setErrorMessage("");
                localStorage.setItem('user_id', data.user_id);
                // console.log(localStorage.getItem('user_id'));
                localStorage.setItem('first_name', data.first_name);
                navigate('/protein-stability');
                // Redirect or handle successful login
            } else {
                setError(data.message || "Login failed");
            }

        } catch (error) {
            setError("An error occurred. Please try again.");
        }
    };

    return (
        <div className='flex flex-col mt-[-50px] rounded-[30px] bg-white w-[400px] h-[480px] shadow-custom z-10 justify-center '>
            <h1 className="font-poppins text-2xl font-medium leading-12 text-center">Log in</h1>
            <p className='font-poppins text-base font-normal leading-6 text-center text-[#666666]'>
                Don't have an account?{' '}
                <span className="underline cursor-pointer" onClick={onSwitchToSignup}>Sign up</span>
            </p>

            <form onSubmit={handleLogin} className="flex flex-col px-8 items-start mt-8 gap-1.5">
                {error && <p className="text-red-500">{error}</p>}
                {success && <p className="text-green-500">{success}</p>}
                
                <Label htmlFor="email" className='text-left text-[#666666]'>Your email</Label>
                <Input
                    type="email"
                    id="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                />
                
                <Label htmlFor="password" className='text-left text-[#666666]'>Your password</Label>
                <Input
                    type="password"
                    id="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />

                <Button type="submit" className='w-full bg-[#95D524] rounded-[27px] mt-4 px-8'>
                    Login
                </Button>
            </form>
        </div>
    );
}

export default Login;

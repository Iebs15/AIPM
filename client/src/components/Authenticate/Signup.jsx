import React, { useState } from 'react'
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from '@/components/ui/button';
import { useNavigate } from 'react-router-dom';

function Signup({ onSwitchToLogin }) {
    const [firstName, setFirstName] = useState('');
    const [lastName, setLastName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();

        // Basic validation
        if (password !== confirmPassword) {
            setError("Passwords do not match!");
            return;
        }

        setError('');  // Clear error if no issues
        try {
            // Send a POST request to the backend
            const response = await fetch('http://52.91.54.146:5000/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    firstName,
                    lastName,
                    email,
                    password
                })
            });

            const data = await response.json();

            if (response.ok) {
                setSuccess("Account created successfully!");
                setError('');  // Clear error
                localStorage.setItem('user_id', data.user_id);
                localStorage.setItem('first_name', data.first_name);
                navigate('/protein-stability');
            } else {
                setError(data.message || "Signup failed");
            }

        } catch (error) {
            setError("An error occurred. Please try again.");
        }
    };

    return (
        <div className='flex flex-col mt-[-50px] rounded-[30px] bg-white w-[400px] h-[480px] shadow-custom z-10 justify-center'>
            <h1 className="font-poppins text-2xl font-medium leading-12 text-center">Create an account</h1>
            <p className='font-poppins text-base font-normal leading-6 text-center text-[#666666]'>
                Already have an account?{' '}
                <span className="underline cursor-pointer" onClick={onSwitchToLogin}>Log in</span>
            </p>

            <p className='font-roboto mt-6 text-base font-normal leading-[21.09px] text-center text-[#666666]'>Enter your email address to create an account.</p>
            
            <form onSubmit={handleSubmit} className="flex flex-col px-8 items-start mt-6 gap-1.5">
                {error && <p className="text-red-500">{error}</p>}
                {success && <p className="text-green-500">{success}</p>}

                {/* First Name and Last Name in one row */}
                <div className="flex w-full gap-4">
                    <div className="flex-1">
                        <Label htmlFor="firstName" className='text-left text-[#666666]'>First Name</Label>
                        <Input
                            type="text"
                            id="firstName"
                            placeholder="First Name"
                            value={firstName}
                            onChange={(e) => setFirstName(e.target.value)}
                            required
                        />
                    </div>
                    <div className="flex-1">
                        <Label htmlFor="lastName" className='text-left text-[#666666]'>Last Name</Label>
                        <Input
                            type="text"
                            id="lastName"
                            placeholder="Last Name"
                            value={lastName}
                            onChange={(e) => setLastName(e.target.value)}
                            required
                        />
                    </div>
                </div>
                
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
                
                <Label htmlFor="cnfpassword" className='text-left text-[#666666]'>Confirm password</Label>
                <Input
                    type="password"
                    id="cnfpassword"
                    placeholder="Confirm Password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                />
                
                <Button type="submit" className='w-full bg-[#95D524] rounded-[27px] mt-4 px-8'>
                    Create an Account
                </Button>
            </form>
        </div>
    );
}

export default Signup;

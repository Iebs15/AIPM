import React from 'react';
import logo from '../assets/Insimine.png';
import { useState } from 'react';
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from '@/components/ui/button';
import Signup from '@/components/Authenticate/Signup';
import Login from '@/components/Authenticate/Login';

function Authenticate() {
    const [showSignup, setShowSignup] = useState(false);
    return (
        <div className='flex flex-col mt-8 ml-8'>
            <div className='flex'>
                <img src={logo} />
            </div>
            <div className=' flex bg-custom-gradient h-[380px] mt-12 rounded-tl-[30px] justify-center rounded-bl-[30px]'>
                <div className='flex flex-row'>
                    <div className='flex flex-col justify-center mr-8'>
                        <h1 className='font-roboto text-4xl font-medium leading-[56.25px] text-right text-white' >Welcome to</h1>
                        <p className='font-roboto text-7xl font-medium leading-[56.25px] text-left text-white'>AI Progression</p>
                        <div className='flex flex-row'>
                            <p className='font-roboto text-7xl font-medium leading-[56.25px] text-left text-white mt-8'>Models:</p>
                            {/* <div class="flex flex-col justify-center ml-4">
                                <div className='flex flex-row'>
                                    <div class="bg-white h-2 w-20 mb-2 rounded-full"></div>
                                    <div class="bg-green-500 h-2 w-16 rounded-full"></div>
                                </div>
                                <div class="bg-white h-2 w-10 mb-2 rounded-full"></div>
                            </div> */}
                        </div>
                    </div>
                    {showSignup ? (
                        <Signup onSwitchToLogin={() => setShowSignup(false)} />
                    ) : (
                        <Login onSwitchToSignup={() => setShowSignup(true)} />
                    )}

                </div>

            </div>
        </div>
    )
}

export default Authenticate
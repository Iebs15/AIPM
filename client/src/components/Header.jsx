import React from 'react';
import logo from '../assets/Insimine.png';
import { CircleUser } from 'lucide-react';

function Header() {
    const name = localStorage.getItem('first_name');
    return (
        <div className='flex flex-row mt-8 mx-8 justify-between'>
            <div className='flex w-[250px]'>
                <img src={logo} />
            </div>
            <div className='flex flex-row gap-x-4'>
                <CircleUser color="#95d524" />
                <text>Hi, {name}</text>

            </div>
        </div>
    )
}

export default Header
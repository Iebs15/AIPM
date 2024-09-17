import React from 'react';
import { useState } from 'react';
import { LogOut, Server, HelpCircle, Globe, Home, ShoppingBag, Box, FileText, Settings, ChevronDown, ChevronRight } from 'lucide-react';
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem } from '@/components/ui/dropdown-menu';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";

import { useNavigate } from 'react-router-dom';

const IconText = ({ icon: Icon, text, onClick }) => (
    <div className="flex items-center space-x-2 cursor-pointer" onClick={onClick}>
        <Icon size={20} />
        <p>{text}</p>
    </div>
);

function Sidebar() {
    const [selectedOption, setSelectedOption] = useState('');

    const [isDropdownOpen, setDropdownOpen] = useState(false);

    const navigate = useNavigate();

    const handleLogout = async () => {
        const user_id = localStorage.getItem('user_id');
        // Clear user_id from localStorage and navigate to the home page
        localStorage.removeItem('user_id');
        navigate('/');
    };

    const toggleDropdown = () => {
        setDropdownOpen(!isDropdownOpen);
    };

    const handleAccordionItemClick = (option) => {
        // Handle option click (e.g., show alert, navigate, etc.)
        alert(`${option} clicked`);
    };
    return (
        <div className='flex flex-col w-[270px] mt-10'>
            <div className='flex flex-col justify-center mx-8'>
                {/* <h1 className="font-roboto text-[20px] font-bold leading-[23.44px] text-left text-[#474747]">
                    About Insimine:
                </h1>
                <p className="font-roboto text-[16px] font-normal leading-[18.75px] text-left text-[#6B6B6B] mt-4">
                    InsiMine is a trusted AI & Analytics-based solutions provider empowering pharmaceutical and healthcare industries to make informed, data-driven decisions.
                </p> */}
            </div>
            <div className='bg-custom-gradient-sidebar w-[200px] h-auto mt-[50px] rounded-tr-[39px] rounded-br-[39px] mr-8'>
                <div className="justify-center space-x-4 ml-12">
                    <div className="overflow-y-auto rounded p-2">
                        <ul className="space-y-2 py-2">
                            <li className="">
                                <a href="/home" className="flex items-center space-x-2 text-white font-normal ">
                                    <Home className="w-6 h-6" />
                                    <span>Home</span>
                                </a>
                            </li>
                            {/* Tools section */}
                            <button className="flex items-center space-x-2" onClick={toggleDropdown}>
                                <Server className="w-6 h-6" color='white' />
                                <span className="text-lg text-white">Tools</span>
                            </button>
                            {isDropdownOpen && (
                                <ul className='ml-6 text-white text-[12px] list-disc'>
                                    <li>
                                        <a href="/protein-stability" className="flex items-center text-white  ">
                                            Protein Stability Predictor
                                        </a>
                                    </li>
                                    <li>
                                        <a href="/drug-repurposing" className="flex items-center text-white">
                                            Drug Repurposing
                                        </a>
                                    </li>
                                    <li>
                                        <a href="/cto" className="flex items-center text-white  ">
                                            Clinical Outcome Prediciton
                                        </a>
                                    </li>
                                    {/* <li>
                                        <a href="#" className="flex items-center text-white  ">
                                            Protein Stability Predictor
                                        </a>
                                    </li> */}
                                </ul>

                            )}


                            {/* How to Use */}
                            <li className="mt-6">
                                <a href="#" className="flex items-center space-x-2 text-white font-normal ">
                                    <HelpCircle className="w-6 h-6" />
                                    <span>How to Use?</span>
                                </a>
                            </li>

                            {/* Know More */}
                            <li className="mt-2">
                                <a href="#" className="flex items-center space-x-2 text-white font-normal ">
                                    <Globe className="w-6 h-6" />
                                    <span>Know More</span>
                                </a>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
            <div className='flex flex-row mt-10 mb-2 fixed ml-10 bottom-6 justify-center cursor-pointer' onClick={handleLogout}>
                <LogOut color='#5F6368' />
                <text className="font-roboto text-[20px] font-normal leading-[23.44px] text-left text-[#5F6368]">Log out</text>
            </div>
        </div>
    )
}

export default Sidebar
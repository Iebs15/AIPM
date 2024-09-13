import React from 'react'
import Header from './Header'
import Sidebar from './Sidebar'
import { Separator } from "@/components/ui/separator"

function Layout({children}) {
  return (
    <div className='flex flex-col'>
        <Header />
        <div className='flex flex-row'>
            <Sidebar />
            <Separator orientation="vertical" className='bg-black' />
            <div className='flex flex-col'>
                {children}
            </div>
        </div>

    </div>
  )
}

export default Layout
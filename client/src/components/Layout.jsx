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






// import React from 'react';
// import Header from './Header';
// import Sidebar from './Sidebar';

// function Layout({ children }) {
//   return (
//     <div className="flex flex-col h-screen overflow-hidden">
//         <Header className="sticky top-0 w-full bg-gray-100 shadow-md" />
//       <div className="flex flex-row flex-1">
//       <Sidebar className="fixed top-0 left-0 h-full bg-gray-800 text-white" />
//         <div className="flex-1 overflow-auto p-4">
//           {children}
//         </div>
//       </div>
//     </div>
//   );
// }

export default Layout;
 
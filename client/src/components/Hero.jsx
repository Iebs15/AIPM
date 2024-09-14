// import { useState } from "react";
// import GradualSpacing from "@/components/magicui/gradual-spacing";
// import BlurFade from "@/components/magicui/blur-fade";
// import ShimmerButton from "@/components/magicui/shimmer-button";


// function Hero() {
//   return (
//     <>
//       <div className="flex flex-col justify-center">
//         {/* <GradualSpacing className='font-nas text-center font-bold pointer-events-none bg-gradient-to-b from-green to-lightBlue bg-clip-text text-9xl font-semibold leading-none text-transparent dark:from-green dark:to-lightBlue' text='InsiMine' duration={5} /> */}
//         <GradualSpacing
//           className="font-nas pb-2 text-8xl text-left  bg-clip-text text-black dark:from-green dark:to-lightBlue"
//           text="Mining Insights for"
//         />
//         <GradualSpacing
//           className="font-nas text-8xl text-left"
//           text="Data Driven Success"
//         />
//         <BlurFade delay={1} inView>
//           <p className="font-nas text-center space-x-1 p-8 mt-8 font-bold px-56">
//             InsiMine is a trusted AI and analytics-based solutions provider
//             empowering pharmaceutical and healthcare industries to make
//             informed, data-driven decisions.
//           </p>
//           <div className="flex flex-row justify-center gap-8 mt-8">
//             <a href="https://insimine.com">
//               <ShimmerButton className="shadow-2xl" background="darkBlue" borderRadius="4px">
//                 <span className="whitespace-pre-wrap text-center text-sm font-medium leading-none tracking-tight text-white dark:from-white dark:to-slate-900/10 lg:text-lg">
//                   Website
//                 </span>
//               </ShimmerButton>
//             </a>

//             {/* <PulsatingButton className='text-black dark:text-white' pulseColor='green'>Book a call</PulsatingButton> */}
//           </div>
//         </BlurFade>
//       </div>
//     </>
//   );
// }

// export default Hero;

import { useState } from "react";
import GradualSpacing from "@/components/magicui/gradual-spacing";
import BlurFade from "@/components/magicui/blur-fade";
import ShimmerButton from "@/components/magicui/shimmer-button";
import ToolsSection from "./ToolSection"; // Assuming ToolsSection is in the same directory

function Hero() {
  return (
    <>
      <div className="flex flex-col justify-center">
        {/* Hero Section Content */}
        <GradualSpacing
          className="font-nas pb-2 text-8xl text-left bg-clip-text text-black dark:from-green dark:to-lightBlue"
          text="Mining Insights for"
        />
        <GradualSpacing
          className="font-nas text-8xl text-left"
          text="Data Driven Success"
        />
        <BlurFade delay={1}>
          <p className="font-nas text-center space-x-1 p-8 mt-8 font-bold px-56">
            InsiMine is a trusted AI and analytics-based solutions provider
            empowering pharmaceutical and healthcare industries to make
            informed, data-driven decisions.
          </p>
          <div className="flex flex-row justify-center gap-8 mt-8">
            <a href="https://insimine.com">
              <ShimmerButton className="shadow-2xl" background="darkBlue" borderRadius="4px">
                <span className="whitespace-pre-wrap text-center text-sm font-medium leading-none tracking-tight text-white dark:from-white dark:to-slate-900/10 lg:text-lg">
                  Website
                </span>
              </ShimmerButton>
            </a>
          </div>
        </BlurFade>

        {/* Adding the Tools Section below the Hero content */}
        <ToolsSection />
      </div>
    </>
  );
}

export default Hero;

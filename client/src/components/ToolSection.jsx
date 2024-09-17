import BlurFade from "@/components/magicui/blur-fade";
import ShimmerButton from "@/components/magicui/shimmer-button"; // Assuming this is the preferred button component

export default function ToolsSection() {
  return (
    <BlurFade delay={1.5}>
      <section className="py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-8xl font-nas text-center mb-8 bg-clip-text text-black dark:from-green dark:to-lightBlue">
            Tools
          </h2>
          <p className="text-left mb-12 max-w-3xl text-black dark:text-white font-nas text-lg mx-auto">
            Unlock the full potential of your data with InsiMine's specialized tools tailored for the
            pharmaceutical and healthcare industries. Our innovative solutions transform raw data into actionable insights,
            driving growth and improving patient outcomes.
          </p>

          <div className="grid md:grid-cols-2 gap-8">
            <ToolCard
              title="Protein Stability"
              description="Leverage advanced algorithms to predict and analyze protein stability, crucial for drug development and optimization."
              offerings={["Stability Prediction", "Mutation Analysis"]}
              href='/protein-stability'
            />
            <ToolCard
              title="Drug Repurposing"
              description="Identify new therapeutic applications for existing drugs, accelerating the drug discovery process and reducing development costs."
              offerings={["Compound Screening", "Target Identification"]}
              href='/drug-repurposing'
            />
          </div>
        </div>
      </section>
    </BlurFade>
  );
}

function ToolCard({ title, description, offerings, href }) {
  return (
    <div className="p-8 rounded-lg border-2 border-black bg-white dark:bg-gray-800">
      <h3 className="text-4xl font-nas font-bold mb-4 text-black dark:text-white">{title}</h3>
      <p className="mb-6 text-lg text-black dark:text-gray-300">{description}</p>
      <h4 className="font-semibold mb-2 text-black dark:text-white">Key offerings:</h4>
      <ul className="mb-6">
        {offerings.map((offering, index) => (
          <li key={index} className="flex items-center mb-2 text-black dark:text-white">
            <svg className="w-4 h-4 mr-2 text-green-500" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                clipRule="evenodd"
              />
            </svg>
            {offering}
          </li>
        ))}
      </ul>
      <div className="flex flex-row justify-center gap-8 mt-8">
        <a href={href}>
          <ShimmerButton
            className="shadow-2xl" background="darkBlue" borderRadius="4px"
          >
            <span className="whitespace-pre-wrap text-center text-sm font-medium leading-none tracking-tight text-white lg:text-lg">
              Learn More
            </span>
          </ShimmerButton>
        </a>
      </div>
    </div>
  );
}

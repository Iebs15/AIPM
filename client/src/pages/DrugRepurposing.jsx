"use client";
import React from 'react';
import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { ChevronLeft, ChevronRight, X, Wrench, Upload, User, Settings } from "lucide-react";
import { diseases } from "@/components/data/Unique_Diseases"; // Array of disease objects
import { drugs } from "@/components/data/Unique_Chemicals"; // Array of drug objects
import Select from "react-select"; // Import react-select

function DrugRepurposing() {
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);
    const [selectedDrugs, setSelectedDrugs] = useState([]); // For selected drugs
    const [selectedDisease, setSelectedDisease] = useState(null); // For selected disease
    const [results, setResults] = useState([]);

    const toggleSidebar = () => setIsSidebarOpen(!isSidebarOpen);

    // Handle drug selection, storing the full drug object
    const handleDrugSelection = (selectedOptions) => {
        setSelectedDrugs(selectedOptions ? selectedOptions.map(opt => opt.value) : []);
    };

    // Remove a selected drug
    const removeDrug = (drug) => {
        setSelectedDrugs(selectedDrugs.filter((d) => d.ChemicalID !== drug.ChemicalID));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        // Prepare the data to be sent to the backend
        const data = {
            disease: selectedDisease, // The selected disease
            drugs: selectedDrugs.map(drug => drug.ChemicalID), // Send only ChemicalIDs
        };

        try {
            // Make a POST request to the Flask backend
            const response = await fetch('http://localhost:5000/getscore', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });

            // Check if the response is OK
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            // Parse the JSON response
            const resultData = await response.json();

            // Remove the known drugs (selectedDrugs) from resultData
            const filteredResults = Object.entries(resultData).filter(([drugID]) =>
                !selectedDrugs.some((drug) => drug.ChemicalID === drugID)
            );

            // Sort by score in descending order
            const sortedResults = filteredResults.sort(([, scoreA], [, scoreB]) => scoreB - scoreA);

            // Pick top 3 drugs excluding input drugs, map ID to chemical names
            const top3Drugs = sortedResults.slice(0, 3).map(([chemicalID, score]) => {
                const drug = drugs.find((d) => d.ChemicalID === chemicalID);
                return {
                    name: drug ? drug.ChemicalName : chemicalID, // Fallback to chemicalID if name not found
                    score
                };
            });

            // Update the results state to display in the table
            setResults(top3Drugs);
        } catch (error) {
            console.error('Error:', error);
        }
    };
    const customStyles = {
        // option: (provided, state) => ({
        //   ...provided,
        //   backgroundColor: state.isSelected ? '#cce5ff' : 'white', // Change background color when selected
        //   borderRadius: state.isSelected ? '12px' : '0', // Add border-radius when selected
        //   color: 'black', // Text color
        // }),
        multiValue: (provided, state) => ({
            ...provided,
            backgroundColor: '#fff', // Background for selected multi-value items
            borderRadius: '12px', // Border-radius for selected multi-value items
            border: '1px solid #ccc', // Border-width and border-color
            boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)', // Add subtle box-shadow
        }),
        multiValueLabel: (provided) => ({
            ...provided,
            color: 'black', // Text color for multi-value items
        }),
        // multiValueRemove: (provided) => ({
        //     ...provided,
        //     color: 'black',
        //     borderRadius: '50%',
        //     border: '1px solid #ccc',
        //     width: '18px', // Adjust size as needed
        //     height: '18px',
        //     display: 'flex',
        //     alignItems: 'center',
        //     justifyContent: 'center',
        //     pa
        //     ':hover': {
        //         backgroundColor: '#ffcccb', // Background color on hover over remove icon
        //         color: 'red',
        //     },
        // }),
    };
    return (
        <div className='flex-1 flex flex-col overflow-hidden transition-all duration-300'>
            <main className="flex-1 overflow-x-hidden overflow-y-hidden ">
                <div className="container w-[800px] mx-auto px-6 py-8">
                    <h1 className="text-3xl font-semibold mb-6">Drug Repurposing</h1>
                    <form onSubmit={handleSubmit} className="space-y-6">
                        {/* Target Disease Selection */}
                        <div>
                            <label className="block text-sm font-medium mb-2" htmlFor="targetDisease">
                                Target Disease
                            </label>
                            <Select
                                options={diseases.map((d) => ({
                                    value: d,
                                    label: d.DiseaseName, // Display DiseaseName
                                }))}
                                onChange={(selectedOption) =>
                                    setSelectedDisease(selectedOption ? selectedOption.value : null)
                                }
                                isSearchable
                                placeholder="Search or enter a disease"
                                isClearable
                                styles={customStyles}
                            />
                        </div>

                        {/* Known Drugs Selection */}
                        <div>
                            <label className="block text-sm font-medium mb-2" htmlFor="knownDrugs">
                                Known Drugs
                            </label>
                            <div className="flex flex-wrap gap-2 mb-2">
                                {selectedDrugs.map((drug) => (
                                    <Badge key={drug.ChemicalID} variant="secondary" className='bg-transparent border-transparent'>
                                        {drug.ChemicalID} {/* Display ChemicalName */}
                                        {/* <Button
                        variant="ghost"
                        size="sm"
                        className="ml-1 h-4 w-4 p-0"
                        onClick={() => removeDrug(drug)}
                      >
                        <X className="h-3 w-3" />
                      </Button> */}
                                    </Badge>
                                ))}
                            </div>
                            <Select
                                options={drugs.map((d) => ({
                                    value: d,
                                    label: `${d.ChemicalName} - (${d.ChemicalID})`, // Display ChemicalID and ChemicalName
                                }))}
                                onChange={handleDrugSelection}
                                isSearchable
                                placeholder="Search or enter a drug"
                                isMulti
                                isClearable
                                styles={customStyles}
                            />
                        </div>

                        <Button className='bg-[#95D524] rounded-[25px]' type="submit">Submit</Button>
                    </form>

                    {/* Results Table */}
                    {/* {results.length > 0 && (
              <div className="mt-8">
                <h2 className="text-2xl font-semibold mb-4">Results</h2>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Drug Name</TableHead>
                      <TableHead>Score</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {results.map((result) => (
                      <TableRow key={result.name}>
                        <TableCell>{result.name}</TableCell>
                        <TableCell>{(result.score * 10000000000000)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )} */}
                    {results.length > 0 && (
                        <div className="mt-8">
                            <fieldset className="border border-[#2AC4F7] p-4 rounded-lg bg-[#2AC4F70D]">
                                <legend><Badge className='text-xl bg-[#2AC4F7]'>Drugs that can be repurposed</Badge></legend>
                                {results.filter(result => result.score !== 0).length > 0 ? (
                                    <Table>
                                        <TableHeader>
                                            <TableRow>
                                                <TableHead>Drug Name</TableHead>
                                                <TableHead>Score</TableHead>
                                            </TableRow>
                                        </TableHeader>
                                        <TableBody>
                                            {results
                                                .filter(result => result.score !== 0) // Filter out results with a score of 0
                                                .map((result) => (
                                                    <TableRow key={result.name}>
                                                        <TableCell>{result.name}</TableCell>
                                                        <TableCell>{(result.score * 10000000000000)}</TableCell>
                                                    </TableRow>
                                                ))}
                                        </TableBody>
                                    </Table>
                                ) : (
                                    <p>No similar drug found</p>  // Display this message if all scores are 0
                                )}
                            </fieldset>
                            {/* <h2 className="text-2xl font-semibold mb-4">Results</h2> */}

                        </div>
                    )}

                </div>
            </main>
        </div>
    )
}

export default DrugRepurposing
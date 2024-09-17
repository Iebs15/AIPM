"use client"

import React, { useState } from 'react'
import { Button } from "@/components/ui/button"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Lock } from "lucide-react"
import { diseases } from "@/components/data/Unique_Diseases"
import { drugs } from "@/components/data/Unique_Chemicals"
import Select from "react-select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export default function DrugRepurposing() {
  const [selectedDrugs, setSelectedDrugs] = useState([])
  const [selectedDisease, setSelectedDisease] = useState(null)
  const [results, setResults] = useState([])

  const handleDrugSelection = (selectedOptions) => {
    setSelectedDrugs(selectedOptions ? selectedOptions.map(opt => opt.value) : [])
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const data = {
      disease: selectedDisease,
      drugs: selectedDrugs.map(drug => drug.ChemicalID),
    }

    try {
      const response = await fetch('http://52.91.54.146:5000/getscore', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        throw new Error('Network response was not ok')
      }

      const resultData = await response.json()
      const filteredResults = Object.entries(resultData).filter(([drugID]) =>
        !selectedDrugs.some((drug) => drug.ChemicalID === drugID)
      )
      const sortedResults = filteredResults.sort(([, scoreA], [, scoreB]) => scoreB - scoreA)
      const top3Drugs = sortedResults.slice(0, 3).map(([chemicalID, score]) => {
        const drug = drugs.find((d) => d.ChemicalID === chemicalID)
        return {
          name: drug ? drug.ChemicalName : chemicalID,
          score
        }
      })
      setResults(top3Drugs)
    } catch (error) {
      console.error('Error:', error)
    }
  }

  const customStyles = {
    control: (provided) => ({
      ...provided,
      minHeight: '38px',
    }),
    menu: (provided) => ({
      ...provided,
      zIndex: 9999, // Ensure dropdown is on top
      position: 'absolute', // Make sure it's not constrained by parent elements
    }),
    menuPortal: (provided) => ({
      ...provided,
      zIndex: 9999, // Extra safety for portal
    }),
    multiValue: (provided) => ({
      ...provided,
      backgroundColor: '#fff',
      borderRadius: '12px',
      border: '1px solid #ccc',
      boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
    }),
    multiValueLabel: (provided) => ({
      ...provided,
      color: 'black',
    }),
  }

  return (
    <div className='flex-1 flex flex-col overflow-hidden transition-all duration-300'>
      <main className="flex-1 overflow-x-hidden overflow-y-auto">
        <div className="container w-[800px] mx-auto px-6 py-8">
          <h1 className="text-3xl font-semibold mb-6">Drug Repurposing</h1>
          <Tabs defaultValue="disease-wise">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="disease-wise">Disease-wise Approach</TabsTrigger>
              <TabsTrigger value="drug-wise" disabled>
                Drug-wise Approach
                <Lock className="ml-2 h-4 w-4" />
              </TabsTrigger>
            </TabsList>
            <TabsContent value="disease-wise">
              <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium mb-2" htmlFor="targetDisease">
                    Target Disease
                  </label>
                  <Select
                    options={diseases.map((d) => ({
                      value: d,
                      label: d.DiseaseName,
                    }))}
                    onChange={(selectedOption) =>
                      setSelectedDisease(selectedOption ? selectedOption.value : null)
                    }
                    isSearchable
                    placeholder="Search or enter a disease"
                    isClearable
                    styles={customStyles}
                    menuPortalTarget={document.body} // Ensure the dropdown is rendered at the top level
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2" htmlFor="knownDrugs">
                    Known Drugs
                  </label>
                  <div className="flex flex-wrap gap-2 mb-2">
                    {selectedDrugs.map((drug) => (
                      <Badge key={drug.ChemicalID} variant="secondary" className='bg-transparent border-transparent'>
                        {drug.ChemicalID}
                      </Badge>
                    ))}
                  </div>
                  <Select
                    options={drugs.map((d) => ({
                      value: d,
                      label: `${d.ChemicalName} - (${d.ChemicalID})`,
                    }))}
                    onChange={handleDrugSelection}
                    isSearchable
                    placeholder="Search or enter a drug"
                    isMulti
                    isClearable
                    styles={customStyles}
                    menuPortalTarget={document.body} // Ensure the dropdown is rendered at the top level
                  />
                </div>
                <Button className='bg-[#95D524] rounded-[25px]' type="submit">Submit</Button>
              </form>
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
                            .filter(result => result.score !== 0)
                            .map((result) => (
                              <TableRow key={result.name}>
                                <TableCell>{result.name}</TableCell>
                                <TableCell>{(result.score * 10000000000000)}</TableCell>
                              </TableRow>
                            ))}
                        </TableBody>
                      </Table>
                    ) : (
                      <p>No similar drug found</p>
                    )}
                  </fieldset>
                </div>
              )}
            </TabsContent>
            <TabsContent value="drug-wise">
              <div className="flex items-center justify-center h-64">
                <p className="text-gray-500">Drug-wise approach is currently unavailable</p>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </main>
    </div>
  )
}

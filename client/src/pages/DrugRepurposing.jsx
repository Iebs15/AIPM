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
import { diseases } from "@/components/data/Unique_Diseases"
import { drugs } from "@/components/data/Unique_Chemicals"
import Select from "react-select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export default function DrugRepurposing() {
  const [selectedDrugs, setSelectedDrugs] = useState([])
  const [selectedDisease, setSelectedDisease] = useState(null)
  const [results, setResults] = useState([])
  const [targetDrug, setTargetDrug] = useState(null)
  const [relatedDiseases, setRelatedDiseases] = useState([])
  const [relatedDrugs, setRelatedDrugs] = useState([])
  const [selectedRelatedDisease, setSelectedRelatedDisease] = useState(null)
  const [allRelatedDrugs, setAllRelatedDrugs] = useState([])

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
      const response = await fetch(`${import.meta.env.VITE_SERVER_URL}/getscore`, {
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

  const handleListRelatedDiseases = async () => {
    if (!targetDrug) return;

    try {
      const response = await fetch(`${import.meta.env.VITE_SERVER}/getrelateddiseases`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ drug: targetDrug }),
      })

      if (!response.ok) {
        throw new Error('Failed to fetch related diseases')
      }

      const data = await response.json()
      if (data.error) {
        throw new Error(data.error)
      }

      // Set the related diseases received from the backend
      setRelatedDiseases(data.diseases)

    } catch (error) {
      console.error('Error fetching related diseases:', error)
    }
  }

  const handleFindDrug = async (disease) => {
    setSelectedRelatedDisease(disease);

    try {
      const response = await fetch(`${import.meta.env.VITE_SERVER_URL}/getdrugsfordisease`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ disease: disease.DiseaseName }),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch related drugs');
      }

      const data = await response.json();

      const drugsArray = Object.entries(data).map(([chemicalID, score]) => {
        const drug = drugs.find((d) => d.ChemicalID === chemicalID);
        return {
          ChemicalName: drug ? drug.ChemicalName : chemicalID,
          Score: score,
        };
      });

      setRelatedDrugs(drugsArray);

    } catch (error) {
      console.error('Error fetching related drugs:', error);
    }
  }

  const handleFindAllDrugs = async () => {
    try {
      const allDrugsPromises = relatedDiseases.map(async (disease) => {
        const response = await fetch(`${import.meta.env.VITE_SERVER_URL}/getdrugsfordisease`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ disease: disease.DiseaseName }),
        });

        if (!response.ok) {
          throw new Error(`Failed to fetch related drugs for ${disease.DiseaseName}`);
        }

        const data = await response.json();

        const drugsArray = Object.entries(data).map(([chemicalID, score]) => {
          const drug = drugs.find((d) => d.ChemicalID === chemicalID);
          return {
            ChemicalName: drug ? drug.ChemicalName : chemicalID,
            Score: score,
          };
        });

        return {
          disease: disease.DiseaseName,
          drugs: drugsArray,
        };
      });

      const allDrugs = await Promise.all(allDrugsPromises);
      setAllRelatedDrugs(allDrugs);

    } catch (error) {
      console.error('Error fetching all related drugs:', error);
    }
  }

  const customStyles = {
    control: (provided) => ({
      ...provided,
      minHeight: '38px',
    }),
    menu: (provided) => ({
      ...provided,
      zIndex: 9999,
      position: 'absolute',
    }),
    menuPortal: (provided) => ({
      ...provided,
      zIndex: 9999,
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
              <TabsTrigger value="drug-wise">Drug-wise Approach</TabsTrigger>
            </TabsList>
            <TabsContent value="disease-wise">
              {/* Disease-wise Approach */}
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
                    menuPortalTarget={document.body}
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
                    menuPortalTarget={document.body}
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
                                <TableCell>{(result.score * 10000000000000).toFixed(2)}</TableCell>
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
              {/* Drug-wise Approach */}
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium mb-2" htmlFor="targetDrug">
                    Target Drug
                  </label>
                  <Select
                    options={drugs.map((d) => ({
                      value: d,
                      label: `${d.ChemicalName} - (${d.ChemicalID})`,
                    }))}
                    onChange={(selectedOption) =>
                      setTargetDrug(selectedOption ? selectedOption.value : null)
                    }
                    isSearchable
                    placeholder="Search or enter a drug"
                    isClearable
                    styles={customStyles}
                    menuPortalTarget={document.body}
                  />
                </div>
                <Button
                  className='bg-[#95D524] rounded-[25px]'
                  onClick={handleListRelatedDiseases}
                  disabled={!targetDrug}
                >
                  List Related Diseases
                </Button>
                {relatedDiseases.length > 0 && (
                  <div className="mt-8">
                    <fieldset className="border border-[#2AC4F7] p-4 rounded-lg bg-[#2AC4F70D]">
                      <legend><Badge className='text-xl bg-[#2AC4F7]'>Related Diseases</Badge></legend>
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Disease Name</TableHead>
                            <TableHead>Action</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {relatedDiseases.map((disease) => (
                            <TableRow key={disease.DiseaseID}>
                              <TableCell>{disease.DiseaseName}</TableCell>
                              <TableCell>
                                <Button
                                  onClick={() => handleFindDrug(disease)}
                                  className='bg-[#95D524] rounded-[25px] text-xs py-1 px-2'
                                >
                                  Find Drug
                                </Button>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                      <div className="mt-4">
                        <Button
                          onClick={handleFindAllDrugs}
                          className='bg-[#95D524] rounded-[25px]'
                        >
                          Find for All Diseases
                        </Button>
                      </div>
                    </fieldset>
                  </div>
                )}
                {selectedRelatedDisease && relatedDrugs.length > 0 && (
                  <div className="mt-8">
                    <fieldset className="border border-[#2AC4F7] p-4 rounded-lg bg-[#2AC4F70D]">
                      <legend><Badge className='text-xl bg-[#2AC4F7]'>Drugs Related to {selectedRelatedDisease.DiseaseName}</Badge></legend>
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Drug Name</TableHead>
                            <TableHead>Score</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {relatedDrugs.map((drug) => (
                            <TableRow key={drug.ChemicalName}>
                              <TableCell>{drug.ChemicalName}</TableCell>
                              <TableCell>{(drug.Score * 10000000000000).toFixed(2)}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </fieldset>
                  </div>
                )}
                {allRelatedDrugs.length > 0 && (
                  <div className="mt-8">
                    <fieldset className="border border-[#2AC4F7] p-4 rounded-lg bg-[#2AC4F70D]">
                      <legend><Badge className='text-xl bg-[#2AC4F7]'>All Related Drugs</Badge></legend>
                      {allRelatedDrugs.map((diseaseData) => (
                        <div key={diseaseData.disease} className="mb-4">
                          <h3 className="text-lg font-semibold mb-2">{diseaseData.disease}</h3>
                          <Table>
                            <TableHeader>
                              <TableRow>
                                <TableHead>Drug Name</TableHead>
                                <TableHead>Score</TableHead>
                              </TableRow>
                            </TableHeader>
                            <TableBody>
                              {diseaseData.drugs.map((drug) => (
                                <TableRow key={drug.ChemicalName}>
                                  <TableCell>{drug.ChemicalName}</TableCell>
                                  <TableCell>{(drug.Score * 10000000000000).toFixed(2)}</TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </div>
                      ))}
                    </fieldset>
                  </div>
                )}
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </main>
    </div>
  )
}

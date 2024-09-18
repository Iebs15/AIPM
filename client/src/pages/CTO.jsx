"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card"

export default function CTO() {
  const [input, setInput] = useState("")
  const [trialData, setTrialData] = useState(null)
  const [probability, setProbability] = useState(null)
  const [manualEntry, setManualEntry] = useState(false) // To track if manual data entry is needed
  const [loading, setLoading] = useState(false) // Loading state for fetch button
  const [loadingPredict, setLoadingPredict] = useState(false) // Loading state for prediction button

  // Handle NCTID change without converting it visually for the user
  const handleNctidChange = (e) => {
    setInput(e.target.value)  // No need to convert to uppercase here
    setTrialData(null)        // Reset trial data and probability when NCTID changes
    setProbability(null)
    setManualEntry(false)
  }

  // Fetch trial data from the backend by NCTID
  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true) // Enable loading state for fetching
    try {
      // Convert the input to uppercase internally before sending to the backend
      
      const response = await fetch(`http://localhost:5000/get-trial-data/${input.toUpperCase()}`)
      if (!response.ok) {
        setManualEntry(true) // If no data, enable manual entry
        setTrialData({
          nctid: input.toUpperCase(),  // Convert input to uppercase for internal handling
          enrollment: "",
          lead_sponsor: "",
        }) // Provide empty fields for user input
        return
      }

      const data = await response.json()

      // Convert "NaN" or "undefined" to empty string for the inputs
      const cleanedData = Object.fromEntries(
        Object.entries(data).map(([key, value]) => [key, value === null || value === 'NaN' ? '' : value])
      )
      
      setTrialData(cleanedData)
      setManualEntry(false) // Disable manual entry when data is found
    } catch (error) {
      alert("Error fetching trial data!")
    } finally {
      setLoading(false) // Disable loading state after fetch completes
    }
  }

  // Update the state when a field changes
  const handleChange = (e, field) => {
    setTrialData({
      ...trialData,
      [field]: e.target.value,
    })
  }

  // Call the backend API for prediction
  const handlePredict = async () => {
    setLoadingPredict(true) // Enable loading state for prediction
    try {
      // Convert the NCTID to uppercase internally before sending the request
      const response = await fetch("http://localhost:5000/predict-outcome", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          nctid: trialData.nctid.toUpperCase(),  // Ensure NCTID is uppercase internally
          enrollment: trialData.enrollment,
          lead_sponsor: trialData.lead_sponsor,
        }),
      })
      const data = await response.json()
      setProbability(data.probability.toFixed(2)) // Set probability to 2 decimal places
    } catch (error) {
      alert("Prediction failed!")
    } finally {
      setLoadingPredict(false) // Disable loading state after prediction completes
    }
  }

  return (
    <div className="min-h-screen w-[800px] flex flex-col items-center justify-center p-4">
      <Card className="w-full">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl sm:text-3xl">Clinical Trial Outcome Prediction</CardTitle>
          <CardDescription className="text-lg">Enter trial details to predict the outcome</CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="px-4 sm:px-6">
            <div className="grid w-full items-center gap-4">
              <div className="flex flex-col space-y-1.5">
                <Label htmlFor="trialDetails" className="text-lg">NCT ID</Label>
                <Input
                  id="trialDetails"
                  placeholder="Enter trial ID"
                  value={input}
                  onChange={handleNctidChange}  // No uppercase conversion here
                  className="text-lg p-6"
                />
              </div>
            </div>
          </CardContent>
          <CardFooter className="flex justify-center">
            <Button 
              type="submit" 
              size="lg" 
              className="w-full sm:w-auto" 
              disabled={loading} // Disable button when loading
            >
              {loading ? "Fetching..." : "Fetch Trial Data"}
            </Button>
          </CardFooter>
        </form>
      </Card>

      {/* If trial data exists or manual entry is enabled */}
      {(trialData || manualEntry) && (
        <Card className="w-full mt-4">
          <CardContent className="px-4 sm:px-6">
            <div className="grid w-full items-center gap-4">
              <div>
                <Label>NCT ID</Label>
                <Input
                  value={trialData?.nctid || input}
                  onChange={(e) => handleChange(e, "nctid")}
                />
              </div>
              <div>
                <Label>Enrollment</Label>
                <Input
                  type="number"
                  value={trialData?.enrollment || ""}
                  onChange={(e) => handleChange(e, "enrollment")}
                />
              </div>
              <div>
                <Label>Lead Sponsor</Label>
                <Input
                  value={trialData?.lead_sponsor || ""}
                  onChange={(e) => handleChange(e, "lead_sponsor")}
                />
              </div>

              {!manualEntry && trialData && (
                <>
                  <div>
                    <Label>Study Type</Label>
                    <Input
                      value={trialData.study_type || ""}
                      onChange={(e) => handleChange(e, "study_type")}
                    />
                  </div>
                  <div>
                    <Label>Drug Interventions</Label>
                    <Input
                      value={trialData.drug_interventions || ""}
                      onChange={(e) => handleChange(e, "drug_interventions")}
                    />
                  </div>
                  <div>
                    <Label>Indications</Label>
                    <Input
                      value={trialData.indications || ""}
                      onChange={(e) => handleChange(e, "indications")}
                    />
                  </div>
                  <div>
                    <Label>Phase</Label>
                    <Input
                      value={trialData.phase || ""}
                      onChange={(e) => handleChange(e, "phase")}
                    />
                  </div>
                  <div>
                    <Label>Smiles</Label>
                    <Input
                      value={trialData.smiless || ""}
                      onChange={(e) => handleChange(e, "smiless")}
                    />
                  </div>
                  <div>
                    <Label>Criteria</Label>
                    <Input
                      value={trialData.criteria || ""}
                      onChange={(e) => handleChange(e, "criteria")}
                    />
                  </div>
                </>
              )}
            </div>
          </CardContent>
          <CardFooter className="flex justify-center">
            <Button 
              onClick={handlePredict} 
              size="lg" 
              className="w-full sm:w-auto" 
              disabled={loadingPredict} // Disable button when loading prediction
            >
              {loadingPredict ? "Predicting..." : "Confirm & Predict Outcome"}
            </Button>
          </CardFooter>
        </Card>
      )}

      {/* Display the prediction result with probability */}
      {probability && (
        <div className="w-full mt-4">
          <div
            className={`p-6 rounded-md text-center text-white font-semibold text-xl ${
              probability > 50 ? "bg-green-500 bg-opacity-80" : "bg-red-500 bg-opacity-60"
            }`}
          >
            {probability}%; This is the probability of clinical trial success.
          </div>
        </div>
      )}
    </div>
  )
}
 
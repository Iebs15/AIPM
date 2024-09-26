import React from 'react';

import { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

function ProteinStability() {
    const [inputSequence, setInputSequence] = useState('');
    const [isLoading, setLoading] = useState(false);
    const [mutatedSequence, setMutatedSequence] = useState('');
    const [showMutateInput, setShowMutateInput] = useState(false);
    const [showModifyTabs, setShowModifyTabs] = useState(false);
    const [replaceSequence, setReplaceSequence] = useState({ start: '', end: '', new: '' });
    const [addSequence, setAddSequence] = useState({ index: '', sequence: '' });
    const [deleteSequence, setDeleteSequence] = useState({ start: '', length: '' });
    const [showInitialElements, setShowInitialElements] = useState(true);
    const [stabilityResult, setStabilityResult] = useState('');
    const [bgColor, setBgColor] = useState('bg-white');
    const handleMutateSequence = () => {
        setShowMutateInput(true);
        setShowModifyTabs(false);
        setShowInitialElements(false);
    };

    const handleModifySequence = () => {
        setShowMutateInput(false);
        setShowModifyTabs(true);
        setShowInitialElements(false);
    };

    const handleModificationDone = () => {
        setShowMutateInput(true);
        setShowModifyTabs(false);
        setShowInitialElements(false);
    };

    const predictStability = async () => {
        try {
            setLoading(true);
            const response = await fetch('http://54.242.63.182:5000/check_score', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ originalProtein: inputSequence, mutatedProtein: mutatedSequence }),
            });

            const data = await response.json();
            if (response.ok) {
                setLoading(false);
                if (data.score >= 0) {
                    setBgColor('bg-light-green');
                    setStabilityResult('Stable');
                } else {
                    setBgColor('bg-light-red');
                    setStabilityResult('Unstable');
                }

            } else {
                setLoading(false);
                setBgColor('bg-white');
                setStabilityResult('Error: Could not predict stability');
            }
        } catch (error) {
            console.error('Error predicting stability:', error);
            setLoading(false);
            setBgColor('bg-white');
            setStabilityResult('Error: Could not predict stability');
        }
    };


    const replaceSequenceHandler = () => {
        const start = parseInt(replaceSequence.start) - 1;
        const end = parseInt(replaceSequence.end) - 1;
        const newSequence = inputSequence.substring(0, start) +
            replaceSequence.new +
            inputSequence.substring(end + 1);
        setMutatedSequence(newSequence);
        handleModificationDone();
    };

    const addSequenceHandler = () => {
        const index = parseInt(addSequence.index) - 1;
        const newSequence = inputSequence.substring(0, index) +
            addSequence.sequence +
            inputSequence.substring(index);
        setMutatedSequence(newSequence);
        handleModificationDone();
    };

    const deleteSequenceHandler = () => {
        const start = parseInt(deleteSequence.start) - 1;
        const length = parseInt(deleteSequence.length);
        const newSequence = inputSequence.substring(0, start) +
            inputSequence.substring(start + length);
        setMutatedSequence(newSequence);
        handleModificationDone();
    };

    const renderIndexedSequence = () => {
        return (
            <div className="mb-4 overflow-x-auto">
                <div className="font-mono whitespace-nowrap">
                    {inputSequence.split('').map((char, index) => (
                        <span key={index} className="inline-block text-center" style={{ width: '20px' }}>
                            {char}
                        </span>
                    ))}
                </div>
                <div className="font-mono whitespace-nowrap text-xs text-muted-foreground">
                    {inputSequence.split('').map((_, index) => (
                        <span key={index} className="inline-block text-center" style={{ width: '20px' }}>
                            {index + 1}
                        </span>
                    ))}
                </div>
            </div>
        );
    };
    return (
        <div className={`flex h-screen ${bgColor}`}>
            <div className="flex-1 p-8 overflow-auto">
                <h1 className="font-roboto text-[64px] font-semibold leading-[75px] text-left text-black mb-4">Protein Stability Predictor</h1>

                {showInitialElements && (
                    
                        <div className="mb-4">
                            <Input
                                className="mb-4"
                                placeholder="Enter intial amino acid sequence"
                                value={inputSequence}
                                onChange={(e) => setInputSequence(e.target.value)}
                            />
                        </div> )}
                        {(
                            <div className="space-x-4 mb-4">
                                <Button className='bg-[#95D524] rounded-[25px]' onClick={handleMutateSequence}>Mutate Sequence Manually</Button>
                                <Button className='bg-[#95D524] rounded-[25px]' onClick={handleModifySequence}>Modify Sequence</Button>
                            </div>
                        )}

                {showMutateInput && (
                    <div className="space-y-4 mb-4">
                        <Input
                            className="mb-4"
                            placeholder="Enter initial amino acid sequence"
                            value={inputSequence}
                        />
                        <Input
                            placeholder="Enter mutated amino acid sequence"
                            value={mutatedSequence}
                            onChange={(e) => setMutatedSequence(e.target.value)}
                        />
                        {/* <Button onClick={predictStability}>Predict Stability</Button> */}
                        {isLoading ? (
                            <>
                                <Button>Predicting....</Button>
                            </>
                        ) : (
                            <Button className='bg-[#95D524] rounded-[25px]' onClick={predictStability}>Predict Stability</Button>
                        )}
                        <div className='mt-4 text-xl font-bold'>{stabilityResult}</div>
                    </div>
                )}

                {showModifyTabs && (
                    <>
                        {renderIndexedSequence()}
                        <Tabs defaultValue="replace" className="w-full mb-4 ">
                            <TabsList className='bg-[#2AC4F74D] rounded-[28px]'>
                                <TabsTrigger className='rounded-[21.5px]'value="replace">Replace Sequence</TabsTrigger>
                                <TabsTrigger className='rounded-[21.5px]' value="add">Add Sequence</TabsTrigger>
                                <TabsTrigger className='rounded-[21.5px]' value="delete">Delete Sequence</TabsTrigger>
                            </TabsList>
                            <TabsContent value="replace" className="space-y-4">
                                <Input
                                    placeholder="Start locus"
                                    value={replaceSequence.start}
                                    onChange={(e) => setReplaceSequence({ ...replaceSequence, start: e.target.value })}
                                />
                                <Input
                                    placeholder="End locus"
                                    value={replaceSequence.end}
                                    onChange={(e) => setReplaceSequence({ ...replaceSequence, end: e.target.value })}
                                />
                                <Input
                                    placeholder="New amino acid sequence"
                                    value={replaceSequence.new}
                                    onChange={(e) => setReplaceSequence({ ...replaceSequence, new: e.target.value })}
                                />
                                <Button className='bg-[#95D524] rounded-[25px]' onClick={replaceSequenceHandler}>Replace</Button>
                            </TabsContent>
                            <TabsContent value="add" className="space-y-4">
                                <Input
                                    placeholder="Locus"
                                    value={addSequence.index}
                                    onChange={(e) => setAddSequence({ ...addSequence, index: e.target.value })}
                                />
                                <Input
                                    placeholder="Sequence to add"
                                    value={addSequence.sequence}
                                    onChange={(e) => setAddSequence({ ...addSequence, sequence: e.target.value })}
                                />
                                <Button className='bg-[#95D524] rounded-[25px]' onClick={addSequenceHandler}>Add</Button>
                            </TabsContent>
                            <TabsContent value="delete" className="space-y-4">
                                <Input
                                    placeholder="Start locus"
                                    value={deleteSequence.start}
                                    onChange={(e) => setDeleteSequence({ ...deleteSequence, start: e.target.value })}
                                />
                                <Input
                                    placeholder="Length"
                                    value={deleteSequence.length}
                                    onChange={(e) => setDeleteSequence({ ...deleteSequence, length: e.target.value })}
                                />
                                <Button className='bg-[#95D524] rounded-[25px]' onClick={deleteSequenceHandler}>Delete</Button>
                            </TabsContent>
                        </Tabs>
                    </>
                )}

                {(!showInitialElements && !showMutateInput && !showModifyTabs) && (
                    <div className="space-y-4 mt-4">
                        <div className="mb-4">
                            <Input
                                placeholder="Enter initial amino acid sequence"
                                value={inputSequence}
                                onChange={(e) => setInputSequence(e.target.value)}
                            />
                        </div>
                        <div className="mb-4">
                            <Input
                                placeholder="Enter mutated amino acid sequence"
                                value={mutatedSequence}
                                onChange={(e) => setMutatedSequence(e.target.value)}
                            />
                        </div>
                        {isLoading ? (
                            <>
                                <Button className='bg-[#95D524] rounded-[25px]'>Predicting....</Button>
                            </>
                        ) : (
                            <Button className='bg-[#95D524] rounded-[25px]' onClick={predictStability}>Predict Stability</Button>
                        )}
                        <div className="mt-4 text-xl font-bold">
                            {stabilityResult}
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}

export default ProteinStability
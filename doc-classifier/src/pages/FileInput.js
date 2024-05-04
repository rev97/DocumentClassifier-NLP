import React, { useState } from 'react';
import { Fragment } from 'react'
import { Disclosure, Menu, Transition } from '@headlessui/react';
import { Bars3Icon, BellIcon, XMarkIcon } from '@heroicons/react/24/outline';


const navigation = [
    { name: 'Home', href: '#', current: true },
    { name: 'Train model', href: '/model', current: false },
]


function classNames(...classes) {
    return classes.filter(Boolean).join(' ')
}
function TextField({label, value, setValue}) {
    return (
        <div className={"flex w-full justify-center items-center px-10 gap-4 py-4"}>
            <label className={"w-1/4 text-2xl font-bold"}>{label}</label>
            <input className={"w-3/4 text-black text-2xl p-2"} value={value} onChange={(e)=>setValue(e.target.value)}/>
        </div>
    )
}
function CheckBoxField({label, value, setValue}) {
    return (
        <div className={"flex w-full items-center px-10 gap-4 py-4"}>
            <label className={"w-1/4 text-2xl font-bold"}>{label}</label>
            <input className={"size-8"} type={"checkbox"} value={value} onChange={(e)=>setValue(e.target.checked)}/>
        </div>
    )
}


function FileField({label, setFile}) {
    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    }
    return (
        <div className={"flex w-full justify-center items-center px-10 gap-4 py-4"}>
            <label className={"w-1/4 text-2xl font-bold"}>{label}</label>
            <input className={"w-3/4 text-2xl p-2 cursor-pointer"} type={"file"} onChange={handleFileChange}/>
        </div>
    )
}



const FileInput = ({ setResponse }) => {
    const [classifiers, setClassifiers] = useState([]);
    const [keywords, setKeywords] = useState({});
    const [pageNumber, setPageNumber] = useState("");
    const [hasPageRange, setHasPageRange] = useState(false);
    const [file, setFile] = useState(null);
    const [useTrainedModel, setUseTrainedModel] = useState(false);
    const [modelFile, setModelFile] = useState(null);// State for using a trained model

    const handleUseModelChange = (e) => {
        setUseTrainedModel(e.target.checked);
    };

    const handleModelFileChange = (e) => {
        setModelFile(e.target.files[0]);
    };
    const validateOutput = (outputJson) => {
        if (outputJson.hasOwnProperty("keywords") && outputJson.hasOwnProperty("classification")) {
            if (Array.isArray(outputJson.keywords))
                return true;
        }
        return false;
    }
    const handleClassifierChange = (e) => {
        if (e.key === 'Enter') {
            const classifier = e.target.value.trim();
            if (classifier) {
                setClassifiers([...classifiers, classifier]);
                e.target.value = ''; // Clear the input field after adding classifier
            }
        }
    };

        const handleWordChange = (e, classifier) => {
            const word = e.target.value;
            setKeywords({ ...keywords, [classifier]: word });
        };


        const handleJsonFileChange = (e) => {
            const file = e.target.files[0]; // Check if files property exists before accessing it
            if (file) {
                setFile(file);

                // Handle autofill from file
                const reader = new FileReader();
                reader.onload = (event) => {
                    const fileContent = event.target.result;
                    if (file.name.endsWith('.json')) {
                        parseJSON(fileContent);
                    } else {
                        alert('Unsupported file format');
                    }
                };
                reader.readAsText(file);
            }
        };


        const parseJSON = (jsonData) => {
            try {
                const formDataJson = JSON.parse(jsonData);

                // Update state with parsed JSON data
                setKeywords(formDataJson.Keywords || {});
                setClassifiers(formDataJson.classifiers || {});
                setHasPageRange(formDataJson['Has Page Range'] === 'Yes');
                setPageNumber(formDataJson['Page Number'] || '');
                setFile(formDataJson.PdfFile)

            } catch (error) {
                console.error('Error parsing JSON:', error);
                // Handle parsing error
            }
        };

    const handleSubmit = async (event) => {
        
        // Function to convert file to base64 string

        const formDataJson = {
            classifiers: classifiers,
            Keywords: keywords,
            'Has Page Range': hasPageRange ? 'Yes' : 'No',
            'Use Trained Model': useTrainedModel ? 'Yes':'No',
            'Page Number': pageNumber,
        };

        // Convert JSON to string
        const jsonString = JSON.stringify(formDataJson, null, 4);

        // Create download link
        const encodedUri = encodeURI('data:text/json;charset=utf-8,' + jsonString);
        const link = document.createElement('a');
        link.setAttribute('href', encodedUri);
        link.setAttribute('download', 'FormData.json');
        document.body.appendChild(link); // Required for Firefox
        link.click();



        event.preventDefault();


        // Constructing form data object
        const formDataObject = {};
        classifiers.forEach((classifier) => {
            formDataObject[classifier] = keywords[classifier] || ''; // If no word entered, set an empty string
        });
        const formData = new FormData();
        formData.append('has_page_range', hasPageRange);
        formData.append('Use Trained Model',useTrainedModel);
        formData.append('page_number', pageNumber);
        formData.append('file', file); // 'file' is the key expected by the server for the file
        formData.append('model_file', modelFile);
        formData.append('keywords', JSON.stringify(formDataObject));
        console.log('Form Data:', formData);

        try {
            const response = await fetch('https://nlpbackend-126e7eaede21.herokuapp.com/api/', {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                const data = await response.json();
                console.log(data);

                if (validateOutput(data)) {
                    alert('File uploaded successfully');
                    setResponse(data);
                } else {
                    alert('Invalid response. Please try again!');
                }

            } else {
                alert('Failed to upload the file');
            }
        } catch (error) {
            console.error('Error:', error);

            alert('An error occurred while uploading the file.');
        }
    }


    return (
        <>
            <Disclosure as="nav" className="bg-gray-800">
                {({ open }) => (
                    <>
                        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                            <div className="flex h-16 items-center justify-between">
                                <div className="flex items-center">
                                    <div className="hidden md:block">
                                        <div className="ml-10 flex items-baseline space-x-4">
                                            {navigation.map((item) => (
                                                <a
                                                    key={item.name}
                                                    href={item.href}
                                                    className={classNames(
                                                        item.current
                                                            ? 'bg-gray-900 text-white'
                                                            : 'text-gray-300 hover:bg-gray-700 hover:text-white',
                                                        'rounded-md px-3 py-2 text-2xl font-medium'
                                                    )}
                                                    aria-current={item.current ? 'page' : undefined}
                                                >
                                                    {item.name}
                                                </a>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                                <div className="-mr-2 flex md:hidden">
                                    {/* Mobile menu button */}
                                    <Disclosure.Button className="relative inline-flex items-center justify-center rounded-md bg-gray-800 p-2 text-gray-400 hover:bg-gray-700 hover:text-white focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-gray-800">
                                        <span className="absolute -inset-0.5" />
                                        <span className="sr-only">Open main menu</span>
                                        {open ? (
                                            <XMarkIcon className="block h-12 w-12" aria-hidden="true" />
                                        ) : (
                                            <Bars3Icon className="block h-12 w-12" aria-hidden="true" />
                                        )}
                                    </Disclosure.Button>
                                </div>
                            </div>
                        </div>

                    </>
                )}
            </Disclosure>

            <div className="w-full min-h-screen p-2 bg-gray-800 text-white items-center justify-center">
                <div className="flex justify-center text-6xl py-10 font-semibold font-serif">Classifier Inputs</div>

                <div className="flex w-full justify-center items-center px-10 gap-4 py-4">
                    <label className="w-1/4 text-2xl font-bold">Enter Classifier</label>
                    <input
                        className="w-3/4 text-black text-2xl p-2"
                        placeholder="Enter Classifiers"
                        onKeyPress={handleClassifierChange}
                    />
                </div>

                {classifiers.map((classifier, index) => (
                    <div key={index} className={"flex w-full justify-center items-center px-10 gap-4 py-4"}>
                        <label className={"w-1/4 text-2xl font-bold"}>{classifier}</label>
                        <input
                            type="text"
                            className={"w-3/4 text-black text-2xl p-2"}
                            value={keywords[classifier] || ""} // Populate the value from the Keywords state
                            onChange={(e) => handleWordChange(e, classifier)}
                            placeholder={`Enter ${classifier} Words...`}
                        />
                    </div>
                ))}

                <CheckBoxField label={"Filter Pages"} value={hasPageRange} setValue={setHasPageRange}/>

                {
                    hasPageRange
                    &&
                    <TextField label={"Page Number"} value={pageNumber} setValue={setPageNumber}/>

                }
                <FileField label={"Choose File"} file={file} setFile={setFile}/>

                <button
                    className="flex justify-center items-center mt-10 rounded-md font-semibold p-4 text-2xl bg-gray-600"
                    style={{width: '80%', maxWidth: '400px'}} // Adjust width as needed
                    onClick={handleSubmit}
                >
                    Submit Data
                </button>
                {/* Use Trained Model Checkbox */}
                <div className="flex w-full items-center px-10 gap-4 py-4">
                    <label className="w-1/4 text-2xl font-bold">Use Trained Model</label>
                    <input
                        type="checkbox"
                        className="size-8"
                        checked={useTrainedModel}
                        onChange={handleUseModelChange}
                    />
                </div>

                {/* Conditionally render Model File Upload if useTrainedModel is true */}
                {useTrainedModel && (
                    <div className="flex w-full justify-center items-center px-10 gap-4 py-4">
                        <label className="w-1/4 text-2xl font-bold">Upload Model File</label>
                        <input
                            id="modelFile"
                            className="w-3/4 text-2xl p-2 cursor-pointer"
                            type="file"
                            onChange={handleModelFileChange}
                        />
                    </div>
                )}

                {/* Model File Upload */}
                {/*{useTrainedModel && (*/}
                {/*    <div className="flex w-full justify-center items-center px-10 gap-4 py-4">*/}
                {/*        <label className="w-1/4 text-2xl font-bold">Upload Model File</label>*/}
                {/*        <input id="modelFile" className="w-3/4 text-2xl p-2 cursor-pointer" type="file" />*/}
                {/*    </div>*/}
                {/*)}*/}

                <div className="flex w-full justify-center items-center px-10 gap-4 py-4">
                    <label className="w-1/4 text-2xl font-bold">Upload Form Data</label>
                    <input className="w-3/4 text-2xl p-2 cursor-pointer" type="file" onChange={handleJsonFileChange}/>
                </div>
            </div>
        </>
    );
};

export default FileInput;

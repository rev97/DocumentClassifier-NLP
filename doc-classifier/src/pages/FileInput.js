import React, { useState } from 'react';

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
        const word = e.target.value.trim();
        setKeywords({ ...keywords, [classifier]: word });
    };

    const handleDownload = () => {
        // Prepare CSV data
        let csvContent = "data:text/csv;charset=utf-8,";

        // Add header row
        csvContent += "Field,Value\n";

        // Add form data rows
        csvContent += `"Keywords","${keywords}"\n`;
        csvContent += `"Has Page Range","${hasPageRange ? 'Yes' : 'No'}"\n`;
        csvContent += `"Page Number","${pageNumber}"\n`;

        // Create download link
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", "FormData.csv");
        document.body.appendChild(link); // Required for Firefox
        link.click();
    };

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        setFile(file);

        // Handle autofill from CSV
        if (file) {
            const reader = new FileReader();
            reader.onload = (event) => {
                const csvData = event.target.result;
                parseCSV(csvData);
            };
            reader.readAsText(file);
        }
    };

    const parseCSV = (csvData) => {
        const lines = csvData.split('\n').map(line => line.trim());
        const data = {};

        lines.forEach(line => {
            const [field, value] = line.split(',');
            data[field] = value;
        });

        // Autofill form fields
        setKeywords(data['Keywords'] || '');
        setHasPageRange(data['Has Page Range'] === 'Yes');
        setPageNumber(data['Page Number'] || '');
    };


    const handleSubmit = async (event) => {
        event.preventDefault();

        // Constructing form data object
        const formDataObject = {};
        classifiers.forEach((classifier) => {
            formDataObject[classifier] = keywords[classifier] || ''; // If no word entered, set an empty string
        });
        const formData = new FormData();
        formData.append('has_page_range', hasPageRange);
        formData.append('page_number', pageNumber);
        formData.append('file', file); // 'file' is the key expected by the server for the file
        formData.append('keywords', JSON.stringify(formDataObject));
        console.log('Form Data:', JSON.stringify(formDataObject));

        try {
            const response = await fetch('http://localhost:8000/api/', {
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
        <div className={"w-full min-h-screen p-2 bg-gray-800 text-white"}>
            <div className={"flex justify-center text-6xl py-10 font-semibold font-serif"}>
                Classifier Inputs
            </div>

            <div className={"flex w-full justify-center items-center px-10 gap-4 py-4"}>
                <label className={"w-1/4 text-2xl font-bold"}>Enter Classifier</label>
                <input className={"w-3/4 text-black text-2xl p-2"} placeholder="Enter Classifiers" onKeyPress={handleClassifierChange} />
            </div>

            <div className={"px-10 flex flex-col justify-center items-center"}>
                {classifiers.map((classifier, index) => (
                    <div key={index} className={"flex w-full justify-center items-center px-10 gap-4 py-4"}>
                        <label className={"w-1/4 text-2xl font-bold"}>{classifier}</label>
                        <input
                            type="text"
                            className={"w-3/4 text-black text-2xl p-2"}
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
                    className={"mt-10 rounded-md font-semibold p-4 text-2xl bg-gray-600 w-fit items-center justify-center"}
                    onClick={handleSubmit}
                >
                    Submit Data
                </button>
                <button
                    className={"mt-10 rounded-md font-semibold p-4 text-2xl bg-gray-600 w-fit items-center justify-center"}
                    onClick={handleDownload}
                >
                    Download Form Data
                </button>

                <FileField label={"Auto Fill"} file={file} setFile={handleFileChange}/>
            </div>
        </div>
    );
};

export default FileInput;

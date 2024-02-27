import {useState} from "react";

function TextField({label, value, setValue}) {
    return (
        <div className={"flex w-full justify-center items-center px-10 gap-4 py-4"}>
            <label className={"w-1/4 text-2xl font-bold"}>{label}</label>
            <input className={"w-3/4 text-black text-2xl p-2"} value={value} onChange={(e)=>setValue(e.target.value)}/>
        </div>
    )
}

function NumberField({label, value, setValue}) {
    return (
        <div className={"flex w-full justify-center items-center px-10 gap-4 py-4"}>
            <label className={"w-1/4 text-2xl font-bold"}>{label}</label>
            <input className={"w-3/4 text-black text-2xl p-2"} type={"number"} value={value} onChange={(e)=>setValue(e.target.value)}/>
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

function FileInput({setResponse}) {
    const [keywords, setKeywords] = useState("");
    const [class1Key, setClass1Key] = useState("");
    const [class2Key, setClass2Key] = useState("");
    const [class3Key, setClass3Key] = useState("");
    const [pageNumber, setPageNumber] = useState(0);
    const [file, setFile] = useState(null);
    const validateOutput = (outputJson) => {
        if (outputJson.hasOwnProperty("keywords") && outputJson.hasOwnProperty("classification")) {
            if (Array.isArray(outputJson.keywords))
                return true;
        }

        return false;
    }
    const uploadData = async (event) => {
        event.preventDefault(); // Prevent the default form submit action

        if (!file) {
            alert('Please select a file first.');
            return;
        }

        const formData = new FormData();
        formData.append('keywords', keywords);
        formData.append('preliminary_keywords', class1Key);
        formData.append('implementation_keywords', class2Key);
        formData.append('advanced_keywords', class3Key);
        formData.append('page_number', pageNumber);
        formData.append('file', file); // 'file' is the key expected by the server for the file

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

            <div className={"px-10 flex flex-col justify-center items-center"}>


                <TextField label={"Keywords"} value={keywords} setValue={setKeywords}/>
                <TextField label={"Preliminary Keywords"} value={class1Key} setValue={setClass1Key}/>
                <TextField label={"Implementation Keywords"} value={class2Key} setValue={setClass2Key}/>
                <TextField label={"Advanced Keywords"} value={class3Key} setValue={setClass3Key}/>
                <NumberField label={"Page Number"} value={pageNumber} setValue={setPageNumber}/>
                <FileField label={"Choose File"} file={file} setFile={setFile}/>

                <button
                    className={"mt-10 rounded-md font-semibold p-4 text-2xl bg-gray-600 w-fit items-center justify-center"}

                    onClick={uploadData}
                >
                    Submit data
                </button>
            </div>

        </div>

    )
}

export default FileInput;
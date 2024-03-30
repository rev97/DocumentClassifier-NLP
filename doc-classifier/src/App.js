import {useState} from "react";
import FileInput from "./pages/FileInput";
import Classification from "./pages/Classification";

function App() {
    const [response, setResponse] = useState(null);
    const resetResponse = () => {setResponse(null)};
    return (
        <div className="App">
            {
                response === null && <FileInput setResponse={setResponse}/>
            }

            {
                response !== null &&  <Classification response={response} resetResponse={resetResponse}/>
            }
        </div>
    );

}

export default App;

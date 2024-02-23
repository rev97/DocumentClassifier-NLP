import {useState} from "react";
import FileInput from "./pages/FileInput";
import Classification from "./pages/Classification";

function App() {
    const [currentPage, setCurrentPage] = useState("classifier"); // takes either input or classifier
    const [count, setCount] = useState(0);
    const togglePage = () => {
        if (currentPage === "input") {
            setCurrentPage("classifier");
        } else {
            setCurrentPage("input");
        }
    }

    const incrementVisitor = () => {
        setCount(count+2);
    }


    return (
        <div className="App">
            {/*<div className={"text-center text-pink-800 text-4xl pb-10"}> My App</div>*/}
            {/*{*/}
            {/*    currentPage === "input" && <FileInput visitorCount={count} addVisitor={incrementVisitor}/>*/}
            {/*}*/}

            {/*{*/}
            {/*    currentPage === "classifier" && <Classification someCount={count}/>*/}
            {/*}*/}

            {/*<div className={"flex w-full pt-10 justify-center gap-4"}>*/}
            {/*    <button*/}
            {/*        className={"p-2 bg-gray-800 text-white"}*/}
            {/*        onClick={togglePage}*/}
            {/*    >*/}
            {/*        Toggle page*/}
            {/*    </button>*/}

            {/*    <button*/}
            {/*        className={"p-2 bg-gray-800 text-white"}*/}
            {/*        onClick={()=>setCount(count+1)}*/}
            {/*    >*/}
            {/*        Increment count*/}
            {/*    </button>*/}
            {/*</div>*/}

            <FileInput/>
        </div>
    );
}

export default App;

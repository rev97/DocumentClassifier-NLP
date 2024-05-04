import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import FileInput from './pages/FileInput';
import Classification from './pages/Classification';
import TrainModel from "./pages/TrainModel";
import TrainOutput from "./pages/TrainOutput";

function App() {
    const [response, setResponse] = useState(null);
    const resetResponse = () => setResponse(null);

    const [trainresponse, settrainresponse] = useState(null);
    const resettrainresponse = () => settrainresponse(null);

    return (
        <Router>
                <Routes>

                    <Route
                        path="/"
                        element={ response === null ? (
                            <FileInput setResponse={setResponse} />
                        ) : (
                            <Classification response={response} resetResponse={resetResponse} />
                        )}
                    />
                    <Route
                        path="/model"
                        element={ trainresponse === null ? (
                            <TrainModel setTrainresponse={settrainresponse} />
                        ) : (
                            <TrainOutput trainresponse={trainresponse} resetTrainresponse={resettrainresponse} />
                        )}
                    />
                </Routes>
        </Router>
    );

}

export default App;

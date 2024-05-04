import React from 'react';
import { saveAs } from 'file-saver';
import WordFrequencyTilesT from './TrainingNumberTiles';

function WordWrap({ word }) {
    return (
        <div className="text-md bg-teal-800 text-white px-4 py-2 rounded-md items-center">
            {word}
        </div>
    );
}

function TrainOutput({ trainresponse, resetTrainresponse }) {
    const { model_file, classification, keywords, bar_data } = trainresponse;

    // Function to handle file download
    const handleDownload = async () => {
        if (model_file && model_file !== 'no file found') {
            try {
                const response = await fetch(
                    `https://nlpbackend-126e7eaede21.herokuapp.com/get-model/?path=${encodeURIComponent(model_file)}`
                );

                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }

                const blob = await response.blob();
                const fileName = model_file.substring(model_file.lastIndexOf('/') + 1);
                saveAs(blob, fileName);
            } catch (error) {
                console.error('Error downloading file:', error);
                alert('Failed to download the model file.');
            }
        } else {
            alert('Model file path is missing or invalid.');
        }
    };

    return (
        <div className="w-full min-h-screen p-2 bg-gray-800 text-white flex flex-col items-center justify-center">
            <div className="text-5xl pb-20 font-semibold font-serif">Training Output</div>

            {model_file === 'no file found' && (
                <div className="text-3xl font-semibold text-red-500 pb-8">
                    Issue with Model Training
                </div>
            )}

            <div className="flex flex-col items-center justify-center w-full max-w-4xl">
                <div className="w-full pb-8">
                    <div className="text-3xl pb-4 font-semibold text-center">Keywords used</div>
                    <div className="flex gap-4 flex-wrap justify-center w-full">
                        {keywords.map((keyword) => (
                            <WordWrap key={keyword} word={keyword} />
                        ))}
                    </div>
                </div>

                <div className="w-full pb-8">
                    <div className="text-3xl pb-4 font-semibold text-center">Word Frequencies</div>
                    <WordFrequencyTilesT wordFrequencies={bar_data['Word Frequencies']} />
                </div>
            </div>

            {/* Button to download pickle file */}
            <button
                className="px-4 py-2 bg-amber-500 mt-8 text-black font-bold text-xl cursor-pointer"
                onClick={handleDownload}
                disabled={!model_file || model_file === 'no file found'}
            >
                Download Pickle File
            </button>

            <div
                className="px-4 py-2 bg-amber-500 mt-8 text-black font-bold text-xl cursor-pointer"
                onClick={() => resetTrainresponse()}
            >
                {'< '} Go Back
            </div>
        </div>
    );
}

export default TrainOutput;

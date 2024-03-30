import {useState} from "react";
import BarChart from "./BarChart";
import WordFrequencyTiles from "./NumberTiles";


function WordWrap({word}) {
    return (
        <div className={"text-2xl bg-teal-800 text-white px-4 py-2 rounded-md"}>
            {word}
        </div>
    )
}


function Classification({response, resetResponse}) {
    const {keywords, classification, output_pdf_path, bar_data} = response;

    const handleOnClick = () => {
        window.open(`http://localhost:8000/view-pdf/?path=${encodeURIComponent(output_pdf_path)}`);
    }

    return (
        <div className={"w-full min-h-screen p-2 bg-gray-800 text-white flex flex-col"}>
            <div className={"flex justify-center text-6xl py-10 font-semibold font-serif"}>
                Classification Output
            </div>

            <div className={"flex flex-row px-10 mt-10 gap-10 flex-1"}>
                <div className={"w-1/2 flex flex-col items-center gap-4"}>
                    <div className={"text-3xl border-2 border-gray-200 h-fit px-4 py-2"}>Document with annotations
                    </div>
                    <div className={"flex min-w-full h-[100%] mb-2"}>
                        <iframe className={"w-full h-full"} src= {`http://localhost:8000/view-pdf/?path=${encodeURIComponent(output_pdf_path)}`} />
                    </div>
                </div>
                <div className={"w-[2px] bg-gray-300 min-h-full my-10"}/>
                <div className={"w-1/2 flex items-center flex-col"}>
                    <div className={"text-3xl mb-16  border-2 border-gray-200 h-fit px-4 py-2"}>Classification Details
                    </div>
                    <div className={"w-full pb-4"}>
                        <div className={"text-3xl pb-4 font-semibold"}>Keywords used</div>
                        <div className={"flex gap-4 flex-wrap w-full justify-items-start"}>
                            {keywords.map(keyword => <WordWrap word={keyword}/>)}
                        </div>
                    </div>

                    <div className={"w-full mt-10 pb-4"}>
                        <div className={"text-3xl pb-4 font-semibold"}>classification</div>
                        <div className={"text-2xl bg-red-600 w-fit px-4 py-2 rounded-md"}>{classification}</div>

                    </div>

                    {/*<div className={"w-full mt-10 pb-4"}>*/}
                    {/*    <div className={"text-3xl pb-4 font-semibold"}>Classification</div>*/}

                    {/*    /!* Display each classification value *!/*/}
                    {/*    {Object.entries(classification).map(([pageNumber, prediction], index) => (*/}
                    {/*        <div key={index} className={"text-2xl bg-red-600 w-fit px-4 py-2 rounded-md mb-2"}>*/}
                    {/*            Page {pageNumber}: {prediction}*/}
                    {/*        </div>*/}
                    {/*    ))}*/}
                    {/*</div>*/}

                    <div>
                        <BarChart metricsData={bar_data}/>
                    </div>
                    <div className={"w-full mt-10 pb-4"}>
                        <div className={"text-3xl pb-4 font-semibold"}>Word Frequencies</div>
                        {/*<h1>Word Frequencies</h1>*/}
                        <WordFrequencyTiles wordFrequencies={bar_data['Word Frequencies']}/>
                    </div>
                </div>
            </div>

            <div className={"flex"}>
                <div
                    className={"px-4 py-2 bg-amber-500 mb-10 ml-10 text-black font-bold text-xl cursor-pointer"}
                    onClick={() => resetResponse()}
                >
                    {"< "} Go Back
                </div>
            </div>


        </div>
    )
}

export default Classification;
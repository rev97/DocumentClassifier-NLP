import React from 'react';

const WordFrequencyTiles = ({ wordFrequencies }) => {
    return (
        <div>
            <div>
                {Object.entries(wordFrequencies).map(([word, frequency]) => {
                    // Calculate background color based on frequency
                    const colorIntensity = Math.min(255, 255 - (frequency * 10));
                    const backgroundColor = `rgb(0, ${colorIntensity}, 0)`;

                    return (
                        <div key={word} style={{ border: '1px solid #ccc', padding: '10px', margin: '5px', display: 'inline-block', backgroundColor, borderRadius: '5px', textAlign: 'center' }}>
                            <div style={{ fontWeight: 'bold' }}>{word}</div>
                            <div style={{ marginTop: '5px' }}>{frequency}</div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default WordFrequencyTiles;

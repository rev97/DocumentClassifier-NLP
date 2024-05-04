import React from 'react';

const WordFrequencyTilesT = ({ wordFrequencies }) => {
    return (
        <div style={{ display: 'flex', justifyContent: 'center', flexWrap: 'wrap' }}>
            {Object.entries(wordFrequencies).map(([word, frequency]) => {
                // Calculate background color based on frequency
                const colorIntensity = Math.min(255, 255 - (frequency * 10));
                const backgroundColor = `rgb(0, ${colorIntensity}, 0)`;

                return (
                    <div
                        key={word}
                        style={{
                            border: '1px solid #ccc',
                            padding: '5px', // Reduced padding
                            margin: '5px',
                            backgroundColor,
                            borderRadius: '5px',
                            textAlign: 'center',
                            minWidth: '100px', // Adjusted minimum width
                            maxWidth: '150px', // Adjusted maximum width
                        }}
                    >
                        <div style={{ fontWeight: 'bold', fontSize: '16px', marginBottom: '5px' }}>{word}</div>
                        <div style={{ fontSize: '14px' }}>{frequency}</div>
                    </div>
                );
            })}
        </div>
    );
};

export default WordFrequencyTilesT;

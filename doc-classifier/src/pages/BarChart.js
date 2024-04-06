import React from 'react';
import Plot from 'react-plotly.js';

const BarChart = ({ metricsData }) => {
    // Exclude 'Word Frequencies' column from metricsData
    const filteredMetricsData = Object.fromEntries(
        Object.entries(metricsData).filter(([key, value]) => key !== 'Word Frequencies')
    );

    // Extracting keys and values from the filtered metrics data
    const metricNames = Object.keys(filteredMetricsData);
    const metricCounts = Object.values(filteredMetricsData);

    // Bar chart data
    const data = [
        {
            type: 'bar',
            x: metricNames,
            y: metricCounts,
            marker: {
                color: 'rgba(75,192,192,0.6)',
                line: {
                    color: 'rgba(75,192,192,1)',
                    width: 1,
                },
            },
        },
    ];

    // Bar chart layout with custom toolbar options and disabled default options
    const layout = {
        title: 'Metrics Bar Chart',
        xaxis: {
            title: 'Metrics',
            tickangle: 0, // Ensures horizontal labels
            tickfont: {
                size: 8, // Adjust font size as needed
            },
        },
        yaxis: { title: 'Count' },
        autosize: true, // Adjusts chart size based on the container size
        margin: {
            l: 40,
            r: 40,
            b: 40,
            t: 80,
        },
    };

    // Configuration to disable default options and keep only download and pan
    const config = {
        modeBarButtonsToRemove: ['pan2d','zoom2d','zoomOut2d','zoomIn2d','select2d','lasso2d','resetScale2d'],
        displaylogo: false
    };

    return (
        <div>
            <Plot data={data} layout={layout} config={config} />
        </div>
    );
};

export default BarChart;

'use client';

import { useEffect, useState } from 'react';
import { fetchHeatmapData } from '../services/api';
import { Globe3D } from './3dGlobe';

export default function Heatmap() {
    const [locations, setLocations] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadHeatmap = async () => {
            try {
                const data = await fetchHeatmapData();
                setLocations(data.data);
            } catch (error) {
                console.error(error);
            } finally {
                setLoading(false);
            }
        };
        loadHeatmap();
        
        // Poll Redis every 10 seconds to watch new dots
        const interval = setInterval(loadHeatmap, 10000);
        return () => clearInterval(interval);
    }, []);

    if (loading) return <div className="text-gray-500">Loading geospatial data...</div>;

    return (
        <>
            <Globe3D
                markers={locations}
                config={{
                atmosphereColor: "#4da6ff",
                atmosphereIntensity: 20,
                bumpScale: 5,
                autoRotateSpeed: 0.3,
                }}
                onMarkerClick={(marker) => {
                console.log("Clicked marker:", marker.label);
                }}
                onMarkerHover={(marker) => {
                if (marker) {
                    console.log("Hovering:", marker.label);
                }
                }}
            />
        </>
    );
}
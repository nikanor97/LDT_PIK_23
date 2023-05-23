import React, {useState} from "react";
import DXFViewer from "./components/DxfViewer";

const ViewDXF = () => {
    const [file, setFile] = useState<File | null>(null);

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) {
            // Handle the selected DXF file
            setFile(file);
        }
    };

    return (
        <div>
            <input type="file" onChange={handleFileChange} />
            {file && (<DXFViewer file={file} />)}
        </div>
    );
};

export default ViewDXF;

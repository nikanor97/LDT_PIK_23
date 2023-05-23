import React, {useEffect} from "react";
import {DxfParser} from "dxf-parser";

type DxfViewerProps = {
  file: File;
};

const DXFViewer = (props: DxfViewerProps) => {
    const parser = new DxfParser();
    const reader = new FileReader();

    useEffect(() => {
        reader.onload = () => {
            const dxf = parser.parseSync(reader.result as string);

            console.log(dxf);
        };

        reader.readAsText(props.file);
    }, [props.file]);

    return <div />;
};

export default DXFViewer;

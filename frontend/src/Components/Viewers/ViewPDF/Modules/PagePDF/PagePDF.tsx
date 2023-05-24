import React from "react";
import {Page} from "react-pdf/dist/esm/entry.webpack";
import {PageProps} from "react-pdf";

type PagePDFProps = {
    index: number,
    pageProps?: PageProps
}

const PagePDF = (props: PagePDFProps) => {
    const {index, pageProps} = props;
    return (
        <Page
            loading={""}
            {...pageProps}
            renderMode="svg"
            pageNumber={index + 1}/>
    );
};

export default PagePDF;

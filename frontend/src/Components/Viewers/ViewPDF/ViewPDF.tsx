import React, {useState} from "react";
import {Document, pdfjs} from "react-pdf/dist/esm/entry.webpack";
import styles from "./ViewPDF.module.less";
import classNames from "classnames";
import PagePDF from "./Modules/PagePDF/PagePDF";
import Scrollbars, {ScrollbarProps} from "react-custom-scrollbars";
import Loading from "@root/Components/Loading/Loading";
import {PageProps} from "react-pdf";

type ViewPDFProps = {
    pathToFile: string,
    corepageStyles?: string,
    scrollBarsProps?: ScrollbarProps,
    pageProps?: PageProps,
}

const ViewPDF = (props: ViewPDFProps) => {
    const [numPages, setNumPages] = useState<number | null>(null);
    const {pathToFile, corepageStyles, pageProps} = props; 
    
    const onDocumentLoadSuccess = ({numPages}: {numPages: number}) => {
        setNumPages(numPages);
    };
 
    return (
        <Scrollbars {...props.scrollBarsProps}>
            <Document
                renderMode="svg"
                file={pathToFile}
                onLoadSuccess={onDocumentLoadSuccess}
                className={classNames(styles.pdf, corepageStyles && corepageStyles)}
                options={{
                    cMapPacked: true,
                    cMapUrl: "cmaps/",
                    verbosity: pdfjs.VerbosityLevel.ERRORS,
                }}
                loading={() => {
                    return (
                        <div className={classNames(styles.loading, corepageStyles && corepageStyles)}>
                            <Loading />
                        </div>
                    );
                }}
                error={() => {
                    return (
                        <div className={styles.error}>
                            <div>При попытке отобразить файл произошла ошибка</div>
                            <div>Попробуйте перезагрузить страницу</div>
                        </div>
                    );
                }}>
                {Array.from(new Array(numPages), (el, index) => (
                    <PagePDF 
                        pageProps={pageProps}
                        index={index} 
                        key={index}/>
                ))}
            </Document>
        </Scrollbars>
    );
};

export default ViewPDF;

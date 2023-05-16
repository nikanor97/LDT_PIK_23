import * as React from "react";

const Spinner = () => {
    return (
        <svg width="64" height="64" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M32 5.33331V16" stroke="#00D98B"/>
            <path d="M32 48V58.6667" stroke="#00D98B"/>
            <path d="M13.1465 13.1467L20.6932 20.6933" stroke="#00D98B"/>
            <path d="M43.3066 43.3066L50.8533 50.8533" stroke="#00D98B"/>
            <path d="M5.33301 32H15.9997" stroke="#00D98B"/>
            <path d="M48 32H58.6667" stroke="#00D98B"/>
            <path d="M13.1465 50.8533L20.6932 43.3066" stroke="#00D98B"/>
            <path d="M43.3066 20.6933L50.8533 13.1467" stroke="#00D98B"/>
        </svg>
    );
};

export default Spinner;

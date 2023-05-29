import React, {useEffect, useState} from "react";
import Controllers from "./Controllers";
import {BrowserRouter as Router} from "react-router-dom";
import styles from "./App.module.less";

const App = () => {    
    return (
        <div className={styles.application}>
            <Router>
                <Controllers.Layout>
                    <Controllers.Routes />
                </Controllers.Layout>
            </Router>
        </div>
    );
};

export default App;

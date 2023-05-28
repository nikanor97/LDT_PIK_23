import React from "react";
import ReactDOM from "react-dom";
import App from "./App";
import {Provider} from "react-redux";
import store from "./Redux/store";
import CheckUserContainer from "./Containers/CheckUserContainer/CheckUserContainer";
import "./index.less";

ReactDOM.render(
    <Provider store={store}>
        <CheckUserContainer>
            <App />
        </CheckUserContainer>
    </Provider>,
    document.getElementById("root")
);

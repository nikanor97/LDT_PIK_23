import {takeLatest, call, put} from "redux-saga/effects";
import Actions from "@actions";
import {PayloadAction} from "@reduxjs/toolkit";
import Api from "@api";
import {iActions} from "@redux/Projects/types";
import React from "react";
import useNotification from "@root/Hooks/useNotification/useNotification";
import {setTimeout} from "timers";
import {iApi} from "@root/types";

const ParseDXF = function* (action: PayloadAction<iActions.parseDXF>) {
    const {payload} = action;
    const notification = useNotification();

    // const data: iApi.Projects.DXFParsedData = {
    //     type: "Гостевой",
    //     config: [
    //         {
    //             title: "Ванная",
    //             value: "bathroom",
    //             x: 14,
    //             y: 19,
    //         },
    //         {
    //             title: "Туалет",
    //             value: "toilet",
    //             x: 37,
    //             y: 48,
    //         },
    //     ]
    // };

    try {
        const {data} = yield call(Api.Projects.parseDXF, payload);
        yield put(Actions.Projects._parseDXFSuccess(data));
        notification({
            type: "info",
            message: "Данные из DXF-файла извлечены"
        });
    } catch (error) {
        yield put(Actions.Projects._parseDXFError());
        notification({
            type: "error",
            message: "При извлечении данных из DXF-файла произошла ошибка"
        });
    }
};

export default function* () {
    yield takeLatest(Actions.Projects.parseDXF, ParseDXF);
}

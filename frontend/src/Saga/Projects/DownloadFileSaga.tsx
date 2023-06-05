import {takeLatest, call, put} from "redux-saga/effects";
import Actions from "@actions";
import {PayloadAction} from "@reduxjs/toolkit";
import {iActions} from "@redux/Projects/types";
import Api from "@api";
import React from "react";
import useNotification from "@root/Hooks/useNotification/useNotification";
import {AxiosResponse} from "axios";

const DownloadFile = function* (action: PayloadAction<iActions.downloadResult>) {
    const {payload} = action;
    const notification = useNotification();

    try {
        const response: AxiosResponse = yield call(Api.Projects.downloadResult, payload);
        const data = response.data;
        if (data) {
            // const file = new File([data], "file.stl");
            // const blob = new Blob([file]);
            
            // const url = window.URL.createObjectURL(blob);
            yield put(Actions.Projects._downloadFileSuccess(data));
            // const link = document.createElement("a");
            // link.href = url;
            // const filename = response.headers["content-disposition"].replace("attachment; filename=", "");
            // link.setAttribute("download", decodeURIComponent(filename));
            // document.body.appendChild(link);
            // link.click();
        }
        notification({
            type: "info",
            message: "Результаты скачаны"
        });
        
    } catch (error) {
        notification({
            type: "error",
            message: "При скачивании результатов произошла ошибка"
        });
        yield put(Actions.Projects._downloadFileError());
    }
};

export default function* () {
    yield takeLatest(Actions.Projects.downloadFile, DownloadFile);
}

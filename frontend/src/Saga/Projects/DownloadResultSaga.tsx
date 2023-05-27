import {takeLatest, call, put} from "redux-saga/effects";
import Actions from "@actions";
import {PayloadAction} from "@reduxjs/toolkit";
import {iActions} from "@redux/Projects/types";
import Api from "@api";
import React from "react";
import useNotification from "@root/Hooks/useNotification/useNotification";
import {AxiosResponse} from "axios";

const DownloadResult = function* (action: PayloadAction<iActions.downloadResult>) {
    const {payload} = action;
    const notification = useNotification();

    try {
        const response: AxiosResponse = yield call(Api.Projects.downloadResult, payload);
        const data = response.data;
        if (data) {
            const blob = new Blob([data]);
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = url;
            const filename = response.headers["content-disposition"].replace("inline; filename*=utf-8''", "");
            link.setAttribute("download", decodeURIComponent(filename));
            document.body.appendChild(link);
            link.click();
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
    }
};

export default function* () {
    yield takeLatest(Actions.Projects.downloadResult, DownloadResult);
}

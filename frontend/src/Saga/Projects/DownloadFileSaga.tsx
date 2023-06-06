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
            yield put(Actions.Projects._downloadFileSuccess(data));
        }
    } catch (error) {
        notification({
            type: "error",
            message: "При скачивании 3D модели произошла ошибка"
        });
        yield put(Actions.Projects._downloadFileError());
    }
};

export default function* () {
    yield takeLatest(Actions.Projects.downloadFile, DownloadFile);
}

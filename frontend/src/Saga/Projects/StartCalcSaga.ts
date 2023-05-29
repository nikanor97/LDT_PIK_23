import {takeLatest, call, put} from "redux-saga/effects";
import Actions from "@actions";
import {PayloadAction} from "@reduxjs/toolkit";
import Api from "@api";
import {iActions} from "@redux/Projects/types";
import React from "react";
import useNotification from "@root/Hooks/useNotification/useNotification";
import {iApi} from "@root/types";
import base64 from "@root/Pages/Lk/Projects/Content/TopBar/Modules/CreateProject/Modules/CreateProjectModal/base64";

const startCalc = function* (action: PayloadAction<iActions.startCalc>) {
    const {payload} = action;
    const notification = useNotification();

    try {
        const {data} = yield call(Api.Projects.startCalc, payload);
        yield put(Actions.Projects._startCalcSuccess(data));
    } catch (error) {
        yield put(Actions.Projects._startCalcError());
        notification({
            type: "error",
            message: "При запуске расчета произошла ошибка"
        });
    }
};

export default function* () {
    yield takeLatest(Actions.Projects.startCalc, startCalc);
}

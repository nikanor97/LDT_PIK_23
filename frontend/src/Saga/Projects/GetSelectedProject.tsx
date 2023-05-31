import {takeLatest, call, put} from "redux-saga/effects";
import Actions from "@actions";
import {PayloadAction} from "@reduxjs/toolkit";
import Api from "@api";
import {iActions} from "@redux/Projects/types";
import React from "react";
import useNotification from "@root/Hooks/useNotification/useNotification";
import {iApi} from "@root/types";

const getSelectedProject = function* (action: PayloadAction<iActions.getSelectedProject>) {
    const {payload} = action;
    const notification = useNotification();

    try {
        const {data} = yield call(Api.Projects.getProjectInfo, payload);
        yield put(Actions.Projects._getSelectedProjectSuccess(data));
    } catch (error) {
        yield put(Actions.Projects._getSelectedProjectError());
        notification({
            type: "error",
            message: "При загрузке проекта произошла ошибка"
        });
    }
};

export default function* () {
    yield takeLatest(Actions.Projects.getSelectedProject, getSelectedProject);
}

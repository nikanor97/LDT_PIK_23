import {takeLatest, call, put} from "redux-saga/effects";
import Actions from "@actions";
import {PayloadAction} from "@reduxjs/toolkit";
import {iActions} from "@redux/Projects/types";
import Api from "@api";
import React from "react";
import useNotification from "@root/Hooks/useNotification/useNotification";

const DeleteProjects = function* (action: PayloadAction<iActions.deleteProjects>) {
    const {payload} = action;
    const notification = useNotification();

    try {
        yield call(Api.Projects.deleteProjects, payload);
        notification({
            type: "info",
            message: "Проекты удалены"
        });
        yield put(Actions.Projects._deleteProjectsSuccess(payload));
        yield put(Actions.Projects.setSelectedProjects([]));
    } catch (error) {
        notification({
            type: "error",
            message: "При удалении проектов произошла ошибка"
        });
    }
};

export default function* () {
    yield takeLatest(Actions.Projects.deleteProjects, DeleteProjects);
}

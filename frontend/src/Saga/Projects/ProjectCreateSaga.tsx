import {takeLatest, call, put} from "redux-saga/effects";
import Actions from "@actions";
import {PayloadAction} from "@reduxjs/toolkit";
import Api from "@api";
import {iActions} from "@redux/Projects/types";
import React from "react";
import useNotification from "@root/Hooks/useNotification/useNotification";

const CreateProject = function* (action: PayloadAction<iActions.createProject>) {
    const {payload} = action;
    const notification = useNotification();

    try {
        yield call(Api.Projects.createProject, payload);
        yield put(Actions.Projects.getProjects());
        payload.onSuccess && payload.onSuccess();
        yield put(Actions.Projects.setCreateModal(false));
        notification({
            type: "info",
            message: "Проект создан"
        });
    } catch (error: any) {
        yield put(Actions.Projects._createProjectError());
        let message = "При создании проект произошла ошибка";
        if (error.response.data.detail) message = error.response.data.detail;
        notification({
            type: "error",
            message
        });
    }
};

export default function* () {
    yield takeLatest(Actions.Projects.createProject, CreateProject);
}

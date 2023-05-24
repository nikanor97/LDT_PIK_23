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
        yield put(Actions.Projects.setCreateModal(false));
        notification({
            type: "info",
            message: "Проект создан"
        });
    } catch (error) {
        yield put(Actions.Projects._createProjectError());
        notification({
            type: "error",
            message: "При создании проект произошла ошибка"
        });
    }
};

export default function* () {
    yield takeLatest(Actions.Projects.createProject, CreateProject);
}

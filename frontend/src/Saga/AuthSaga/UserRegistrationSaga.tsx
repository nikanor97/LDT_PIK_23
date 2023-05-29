import {takeLatest, call, put} from "redux-saga/effects";
import Actions from "@actions";
import {PayloadAction} from "@reduxjs/toolkit";
import Api from "@api";
import {iActions} from "@redux/Auth/types";
import React from "react";
import useNotification from "@root/Hooks/useNotification/useNotification";

const UserRegistration = function* (action: PayloadAction<iActions.userRegistration>) {
    const {payload} = action;
    const notification = useNotification();

    try {
        yield call(Api.Auth.registration, payload);
        yield put(Actions.Auth._userRegistrationSuccess());
        action.payload.redirect();
        notification({
            type: "info",
            message: "Вы успешно зарегистрированы"
        });
    } catch (error: any) {
        action.payload.setFieldsErrors(error.response.data);
        notification({
            type: "error",
            message: "При регистрации произошла ошибка"
        });
        yield put(Actions.Auth._userRegistrationError());
    }
};

export default function* () {
    yield takeLatest(Actions.Auth.userRegistration, UserRegistration);
}

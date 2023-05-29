import {createSlice, PayloadAction} from "@reduxjs/toolkit";
import {iActions, iState} from "./types";
import {getShortState, requestStart, requestSuccess, requestError} from "@root/Utils/Redux/getRequestState";

const initialState:iState.Value = {
    registration: getShortState(),
    login: getShortState(),
};

const Slice = createSlice({
    initialState,
    name: "Auth",
    reducers: {
        userLogin: (state, action: PayloadAction<iActions.userLogin>) => {
            requestStart(state.login);
        },
        _userLoginSuccess: (state) => {
            requestSuccess(state.login);
        },
        _userLoginError: (state) => {
            requestError(state.login);
        },
        userRegistration: (state, action: PayloadAction<iActions.userRegistration>) => {
            requestStart(state.registration);
        },
        _userRegistrationSuccess: (state) => {
            requestSuccess(state.registration);
        },
        _userRegistrationError: (state) => {
            requestError(state.registration);
        }
    }
});

export const Actions = Slice.actions;
export default Slice.reducer;

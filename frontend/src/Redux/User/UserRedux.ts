import {createSlice, PayloadAction} from "@reduxjs/toolkit";
import {iApi} from "@types";
import {iActions} from "./types";

type iState = {
    info: iApi.User.iUserInfo | null;
    fetching?: boolean,
}

const initialState:iState  = {
    info: null,
    fetching: true,
};

const Slice = createSlice({
    initialState,
    name: "User",
    reducers: {
        getUserInfo: (state) => {
            return state;
        },
        _getUserInfoSuccess: (state, action:PayloadAction<iActions._getUserInfoSuccess>) => {
            state.info = action.payload;
        },
        _getUserInfoError: (state, action:PayloadAction<iActions._getUserInfoError>) => {
            state.info = action.payload;
        },
        setFetching: (state, action: PayloadAction<iActions.setFetching>) => {
            state.fetching = action.payload;
        },
    }
});

export const Actions = Slice.actions;
export default Slice.reducer;

import {createSlice, PayloadAction} from "@reduxjs/toolkit";
import {iApi} from "@types";
import {iActions} from "./types";

type iState = {
    info: iApi.User.iUserInfo | null;
    users: iApi.Users.Item[] | null;
    fetching?: boolean,
    getUsersFetching: boolean,
}

const initialState:iState  = {
    info: null,
    fetching: true,
    users: null,
    getUsersFetching: false
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
        getUsersAll: (state) => {
            state.getUsersFetching = true;
        },
        _getUserAllSuccess: (state, action: PayloadAction<iActions._getUsersAllSuccess>) => {
            state.getUsersFetching = false;
            state.users = action.payload;
        },
        _getUserAllError: (state) => {
            state.getUsersFetching = false;
        }
    }
});

export const Actions = Slice.actions;
export default Slice.reducer;

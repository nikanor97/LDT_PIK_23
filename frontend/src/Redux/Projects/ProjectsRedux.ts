import {createSlice, PayloadAction} from "@reduxjs/toolkit";
import {iApi} from "@types";
import {iActions} from "./types";

type iState = {
    projects: null | iApi.Projects.Item[];
    selectedProject: null | iApi.Projects.Item;
    createModal: boolean;
    createFetching: boolean;
    getSelectedProject: boolean;
    getFetching: boolean;
    selectedProjects: null | iApi.Projects.Item[];
}

const initialState:iState  = {
    projects: null,
    selectedProject: null,
    createModal: false,
    createFetching: false,
    getSelectedProject: false,
    getFetching: false,
    selectedProjects: null
};

const Slice = createSlice({
    initialState,
    name: "Projects",
    reducers: {
        createProject: (state, action:PayloadAction<iActions.createProject>) => {
            state.createFetching = true;
        },
        _createProjectSuccess: (state, action:PayloadAction<iActions._createProjectSuccess>) => {
            state.createFetching = false;
            if (state.projects) state.projects.unshift(action.payload);
            else state.projects = [action.payload];
        },
        _createProjectError: (state) => {
            state.createFetching = false;
        },
        getSelectedProject: (state, action:PayloadAction<iActions.getSelectedProject>) => {
            state.getSelectedProject = true;
        },
        _getSelectedProjectSuccess: (state, action:PayloadAction<iActions._getSelectedProjectSuccess>) => {
            state.selectedProject = action.payload;
            state.getSelectedProject = false;
        },
        _getSelectedProjectError: (state) => {
            state.getSelectedProject = false;
        },
        setSelectedProject: (state, action: PayloadAction<iActions.setSelectedProject>) => {
            state.selectedProject = action.payload;
        },
        setCreateModal: (state, action: PayloadAction<iActions.setCreateModal>) => {
            state.createModal = action.payload;
        },
        getProjects: (state) => {
            state.getFetching = true;
        },
        _getProjectsSuccess: (state, action:PayloadAction<iActions._getProjectsSuccess>) => {
            state.projects = action.payload;
            state.getFetching = false;
        },
        _getProjectsError: (state) => {
            state.projects = null;
            state.getFetching = false;
        },
        setSelectedProjects: (state, action: PayloadAction<iActions.setSelectedProjects>) => {
            state.selectedProjects = action.payload;
        },
        eraseSelectedProjects: (state) => {
            state.selectedProjects = null;
        },
    }
});

export const Actions = Slice.actions;
export default Slice.reducer;

import {createSlice, PayloadAction} from "@reduxjs/toolkit";
import {iApi} from "@types";
import {iActions} from "./types";

type iState = {
    projects: null | iApi.Projects.Item[];
    selectedProject: null | iApi.Projects.ItemDetail;
    createModal: boolean;
    createFetching: boolean;
    getSelectedProject: boolean;
    getFetching: boolean;
    selectedProjects: null | React.Key[];
    fittingsGroups: iApi.Projects.FittingGroup[] | null;
    getFittings: boolean,
    selectedOption: iApi.Projects.Results | null,
    parseDXFStatus: "loading" | "success" | "error" | null;
    DXFdata: iApi.Projects.DXFParsedData | null,
    startCalcStatus: "loading" | "success" | "error" | null;
    loadingDownload: boolean;
    file: File | null;
    loadFile: boolean,
    tableConfig: {
        currentPage: number;
        defaultPageSize: number;
    } | null,
    statistics: iApi.Statistic.Item | null;
    statisticsFetching: boolean;
    statisticsError: boolean;
}

const initialState:iState  = {
    projects: null,
    selectedProject: null,
    createModal: false,
    createFetching: false,
    getSelectedProject: false,
    getFetching: false,
    selectedProjects: null,
    fittingsGroups: null,
    getFittings: false,
    selectedOption: null,
    parseDXFStatus: null,
    DXFdata: null,
    startCalcStatus: null,
    loadingDownload: false,
    file: null,
    loadFile: false,
    tableConfig: null,
    statistics: {
        avg_n_fittings: 0,
        avg_sewer_length: 0,
        devices: []
    },
    statisticsFetching: false,
    statisticsError: false,
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
        getFittings: (state) => {
            state.getFittings = true;
        },
        _getFittingsSuccess: (state, action: PayloadAction<iActions._getFittingSuccess>) => {
            state.fittingsGroups = action.payload;
            state.getFittings = false;
        },
        _getFittingsError: (state) => {
            state.getFittings = false;
        },
        setSelectedOption: (state, action: PayloadAction<iActions.setSelectedOption>) => {
            state.selectedOption = action.payload;
        },
        parseDXF: (state, action: PayloadAction<iActions.parseDXF>) => {
            state.parseDXFStatus = "loading";
        },
        _parseDXFSuccess: (state, action: PayloadAction<iActions._parseDXFSuccess>) => {
            state.parseDXFStatus = "success";
            state.DXFdata = action.payload;
        },
        _parseDXFError: (state) => {
            state.parseDXFStatus = "error";
        },
        eraseDXFData: (state) => {
            state.DXFdata = null;
            state.parseDXFStatus = null;
        },
        startCalc: (state, action: PayloadAction<iActions.startCalc>) => {
            state.startCalcStatus = "loading";
        },
        _startCalcSuccess: (state, action: PayloadAction<iActions._startCalcSuccess>) => {
            state.startCalcStatus = "success";
            state.selectedProject = action.payload;
        },
        _startCalcError: (state) => {
            state.startCalcStatus = "error";
        },
        downloadResult: (state, action: PayloadAction<iActions.downloadResult>) => {
            state.loadingDownload = true;
        },
        _downloadResultSuccess: (state) => {
            state.loadingDownload = false;
        },
        _downloadResultError: (state) => {
            state.loadingDownload = false;
        },
        downloadFile: (state, action: PayloadAction<iActions.downloadResult>) => {
            state.loadFile = true;
        },
        _downloadFileSuccess: (state, action: PayloadAction<iActions._downloadFileSuccess>) => {
            state.file = action.payload;
            state.loadFile = false;
        },
        _downloadFileError: (state) => {
            state.loadFile = false;
        },
        eraseFile: (state) => {
            state.file = null;
        },
        deleteProjects: (state, action: PayloadAction<iActions.deleteProjects>) => {
            return state;
        },
        _deleteProjectsSuccess: (state, action: PayloadAction<iActions._deleteProjectsSuccess>) => {
            if (state.projects) {
                state.projects = state.projects.filter((item: iApi.Projects.Item) => !action.payload.includes(item.id));
            }
        },
        setTableConfig: (state, action: PayloadAction<iActions.setTableConfig>) => {
            state.tableConfig = action.payload.config;
        },
        eraseTaskConfig: (state) => {
            state.tableConfig = null;
        },
        getStatistics: (state) => {
            state.statisticsFetching = true;
        },
        _getStatisticsSuccess: (state, action: PayloadAction<iActions._getStatisticsSuccess>) => {
            state.statistics = action.payload;
            state.statisticsError = false;
            state.statisticsFetching = false;
        },
        _getStatisticsError: (state) => {
            state.statisticsError = true;
            state.statisticsFetching = false;
        },
        
    }
});

export const Actions = Slice.actions;
export default Slice.reducer;

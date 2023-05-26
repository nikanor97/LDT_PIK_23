import Request from "../Request";
import {Projects} from "./types";
import Endpoints from "./endpoints";

export default {
    createProject: (params: Projects.iCreateProject) => {
        return Request.post<Projects.oCreateProject>(`${Endpoints.base}`, params);
    },
    getProjects: () => {
        return Request.get<Projects.oGetProjects[]>(`${Endpoints.base}`);
    },
    getFittingsGroup: () => {
        return Request.get<Projects.oGetFittingsGroups>(`${Endpoints.getFittings}`);
    },
    getProjectInfo: (params: Projects.iGetProjectInfo) => {
        const url = Endpoints.getProjectInfo.replace("{projectID}", params.id.toString());
        return Request.get<Projects.oGetProjectInfo>(url);
    }
};

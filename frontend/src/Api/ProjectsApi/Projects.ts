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
    },
    parseDXF: (params: Projects.iParseDXF) => {
        const fileData = new FormData();
        fileData.append("dxf", (params.dxf));
        fileData.append("project", params.project.toString());
        return Request.post<Projects.oParseDXF>(`${Endpoints.parseDXF}`, fileData);
    },
    startCalc: (params: Projects.iStartCalc) => {
        return Request.get<Projects.oStartCalc>(`${Endpoints.startCalc}`, params);
    }
};

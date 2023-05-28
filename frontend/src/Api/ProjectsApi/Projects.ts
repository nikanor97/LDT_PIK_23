import Request from "../Request";
import {Projects} from "./types";
import Endpoints from "./endpoints";

export default {
    createProject: (params: Projects.iCreateProject) => {
        return Request.post<Projects.oCreateProject>(`${Endpoints.createProject}`, params);
    },
    getProjects: () => {
        return Request.get<Projects.oGetProjects[]>(`${Endpoints.getProjects}`);
    },
    getFittingsGroup: () => {
        return Request.get<Projects.oGetFittingsGroups>(`${Endpoints.getFittings}`);
    },
    getProjectInfo: (params: Projects.iGetProjectInfo) => {
        const url = Endpoints.getProjectInfo;
        return Request.get<Projects.oGetProjectInfo>(url, {
            project_id: params.id
        });
    },
    parseDXF: (params: Projects.iParseDXF) => {
        const fileData = new FormData();
        fileData.append("dxf", (params.dxf));
        fileData.append("project", params.project.toString());
        return Request.post<Projects.oParseDXF>(`${Endpoints.parseDXF}`, fileData);
    },
    startCalc: (params: Projects.iStartCalc) => {
        return Request.get<Projects.oStartCalc>(`${Endpoints.startCalc}`, params);
    },
    downloadResult: (params: Projects.iDownloadResult) => {
        const url = Endpoints.downloadResult;
        return Request.get(
            url,
            params,
            {
                responseType: "blob"
            }
        );
    },
};

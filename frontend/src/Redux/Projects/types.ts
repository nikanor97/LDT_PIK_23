import {iApi} from "@types";

export declare namespace iActions {
    type setCreateModal = boolean;
    type createProject = {
        performer: string[],
        fittings: string[],
        type: string,
        title: string,
        onSuccess: () => void
    };
    type _createProjectSuccess = iApi.Projects.Item;
    type _getProjectsSuccess = iApi.Projects.Item[];
    type deleteProject = Pick<iApi.Projects.Item, "id">;
    type setSelectedProject = iApi.Projects.Item | null;
    type getSelectedProject =  Pick<iApi.Projects.Item, "id">;
    type _getSelectedProjectSuccess = iApi.Projects.Item;
    type setSelectedProjects = iApi.Projects.Item[];
    type _getFittingSuccess = iApi.Projects.FittingGroup[];
}

import {iApi} from "@types";

export declare namespace Projects {
    // TODO Типизировать
    type iCreateProject = {
        performer: string[],
        fittings: string[],
        type: string,
        title: string,
    };
    type oCreateProject = iApi.Projects.Item;
    type oGetProjects = iApi.Projects.Item[];
    type oGetFittingsGroups = iApi.Projects.FittingGroup[];
    type iGetProjectInfo = Pick<iApi.Projects.Item, "id">
    type oGetProjectInfo = iApi.Projects.ItemDetail;
}

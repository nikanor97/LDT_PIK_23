import {iApi} from "@types";
import {RcFile} from "antd/lib/upload";

export declare namespace iActions {
    type setCreateModal = boolean;
    type createProject = {
        worker_id: string,
        fittings_ids: string[],
        type: string,
        name: string,
        onSuccess: () => void
    };
    type _createProjectSuccess = iApi.Projects.Item;
    type _getProjectsSuccess = iApi.Projects.Item[];
    type deleteProject = Pick<iApi.Projects.Item, "id">;
    type setSelectedProject = iApi.Projects.ItemDetail | null;
    type getSelectedProject =  Pick<iApi.Projects.Item, "id">;
    type _getSelectedProjectSuccess = iApi.Projects.ItemDetail;
    type setSelectedProjects = iApi.Projects.Item[];
    type _getFittingSuccess = iApi.Projects.FittingGroup[];
    type setSelectedOption = number | null;
    type parseDXF = {
        dxf: RcFile,
        project_id: string
    };
    type _parseDXFSuccess = iApi.Projects.DXFParsedData;
    type startCalc = {
        project: number,
        values: {
                deviceType: string,
                X: number,
                Y: number,
                Z: number
            }[]
            
    };
    type _startCalcSuccess = iApi.Projects.ItemDetail;
    type downloadResult = {
        project: string,
        variant: number,
        file_type: "xls" | "stl"
    }
}

import {iApi} from "@types";
import {RcFile} from "antd/lib/upload";

export declare namespace Projects {
    // TODO Типизировать
    type iCreateProject = {
        worker_id: string,
        fittings_ids: string[],
        type: string,
        name: string,
    };
    type oCreateProject = iApi.Projects.Item;
    type oGetProjects = iApi.Projects.Item[];
    type oGetFittingsGroups = iApi.Projects.FittingGroup[];
    type iGetProjectInfo = Pick<iApi.Projects.Item, "id">
    type oGetProjectInfo = iApi.Projects.ItemDetail;
    type iParseDXF = {
        dxf: RcFile,
        project_id: string
    }
    //TODO TYpe
    type oParseDXF = iApi.Projects.DXFParsedData;
    type iStartCalc = {
        project: number,
        values: {
                deviceType: string,
                X: number,
                Y: number,
                Z: number
            }[]
            
    };
    type oStartCalc = iApi.Projects.ItemDetail;
    type iDownloadResult = {
        project: string,
        variant: number,
        file_type: "xls" | "stl"
    }
}

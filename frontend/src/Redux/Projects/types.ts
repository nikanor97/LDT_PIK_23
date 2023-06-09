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
    type setSelectedProjects = React.Key[];
    type _getFittingSuccess = iApi.Projects.FittingGroup[];
    type setSelectedOption = iApi.Projects.Results | null;
    type parseDXF = {
        dxf: RcFile,
        project_id: string
    };
    type _parseDXFSuccess = iApi.Projects.DXFParsedData;
    type startCalc = {
        project_id: string,
        dxf_file_id: string,
        devices: {
                type: string,
                coord_x: number,
                coord_y: number,
                coord_z: number
            }[]
            
    };
    type _startCalcSuccess = iApi.Projects.ItemDetail;
    type downloadResult = {
        project_id: string,
        variant_num: number,
        file_type: "excel" | "stl"
    }
    type _downloadFileSuccess = File;
    type deleteProjects = React.Key[];
    type _deleteProjectsSuccess = React.Key[];
    type setTableConfig = {
        config: {
            currentPage: number;
            defaultPageSize: number;
        }
    }
    type _getStatisticsSuccess = iApi.Statistic.Item;
}

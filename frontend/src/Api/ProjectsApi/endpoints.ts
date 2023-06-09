export default {
    base: "/v1/projects",
    createProject: "/v1/projects/project",
    getProjects: "/v1/projects/projects-all",
    getFittings: "/v1/projects/fittings-all",
    getProjectInfo: "/v1/projects/project",
    parseDXF: "/v1/projects/dxf-upload?project_id={projectID}",
    startCalc: "/v1/projects/result",
    downloadResult: "v1/projects/export",
    deleteProjects: "/v1/projects/delete",
    getStats: "/v1/projects/stats"
};

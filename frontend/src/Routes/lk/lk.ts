const getLkRoutes = (prefix: string = "") => {
    const lkprefix = `${prefix}/lk`;
    const staticRoutes = {
        root: lkprefix,
        projects: `${lkprefix}/projects`,
    };
    const result = {
        ...staticRoutes,
        project: {
            root: (id: string = ":projectID") => `${staticRoutes.projects}/${id}`,
        }
    };
    return result;
};

export default getLkRoutes;

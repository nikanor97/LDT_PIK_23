const getAuthRoutes = (prefix:string = "") => {
    const lprefix = `${prefix}/auth`;
    return {
        root: lprefix,
        login: `${lprefix}/login`,
        registration: `${lprefix}/registration`,
    };
};

export default getAuthRoutes;

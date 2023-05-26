import getAuthRoutes from "./auth/auth";
import getLkRoutes from "./lk/lk";

export const routes = {
    auth: getAuthRoutes(),
    lk: getLkRoutes(),
};

export default routes;

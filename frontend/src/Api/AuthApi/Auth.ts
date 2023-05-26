import Request from "../Request";
import {Auth} from "./types";
import Cookies from "universal-cookie";
import Endpoints from "./endpoints";

const cookies = new Cookies();

export default {
    registration: (params: Auth.iRegistration) => Request.post<Auth.oRegistration>(`${Endpoints.registration}`, {
        name: params.name,
        email: params.email,
        password: params.password
    }),
    login: (params: Auth.iLogin) => Request.post<Auth.oLogin>(`${Endpoints.auth}`, params),
    refresh: (refresh: Auth.iRefresh) => {
        const url = Endpoints.refresh.replace("{refreshToken}", refresh);
        return Request.post<Auth.oRefresh>(url)
            .then(({data}) => {
                const currentDate = new Date();
                cookies.set(
                    "access_token",
                    data.access_token,
                    {
                        expires: new Date(currentDate.getTime() + (data.access_expires_at * 1000)),
                        path: "/",
                    });
                cookies.set(
                    "refresh_token",
                    data.refresh_token,
                    {
                        expires: new Date(currentDate.getTime() + (data.refresh_expires_at * 1000)),
                        path: "/"
                    });
            })
            .catch(() => {
                cookies.remove("refresh_token", {path: "/"});
            });
    }
};

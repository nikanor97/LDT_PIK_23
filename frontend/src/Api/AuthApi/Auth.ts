import Request from "../Request";
import {Auth} from "./types";
import Cookies from "universal-cookie";
import Endpoints from "./endpoints";

const cookies = new Cookies();

export default {
    registration: (params: Auth.iRegistration) => Request.post<Auth.oRegistration>(`${Endpoints.registration}`, params),
    login: (params: Auth.iLogin) => Request.post<Auth.oLogin>(`${Endpoints.auth}`, params),
    refresh: (refresh: Auth.iRefresh) => {
        return Request.post<Auth.oRefresh>(`${Endpoints.refresh}`, {refresh})
            .then(({data}) => {
                cookies.set(
                    "access",
                    data.access_token,
                    {
                        // TODO Пока нет SSL сертификата, убираю это
                        // secure: true,
                        expires: new Date(data.access_expires_at * 1000),
                        path: "/",
                    });
                cookies.set(
                    "refresh",
                    data.refresh_token,
                    {
                        expires: new Date(data.refresh_expires_at * 1000),
                        path: "/"
                    });
            })
            .catch(() => {
                cookies.remove("refresh", {path: "/"});
            });
    }
};

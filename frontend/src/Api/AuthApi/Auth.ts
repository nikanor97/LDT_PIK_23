import Request from "../Request";
import {Auth} from "./types";
import Cookies from "universal-cookie";
import Endpoints from "./endpoints";
import {decode, jwtToken} from "@utils/JWT/decode";

const cookies = new Cookies();

export default {
    registration: (params: Auth.iRegistration) => Request.post<Auth.oRegistration>(`${Endpoints.registration}`, params),
    login: (params: Auth.iLogin) => Request.post<Auth.oLogin>(`${Endpoints.auth}`, params),
    refresh: (refresh: Auth.iRefresh) => {
        return Request.post<Auth.oRefresh>(`${Endpoints.refresh}`, {refresh})
            .then(({data}) => {
                const decodedAccess:jwtToken = decode(data.access);
                cookies.set(
                    "access",
                    data.access,
                    {
                        expires: new Date(decodedAccess.exp * 1000),
                        path: "/"
                    });
                const decodedRefresh:jwtToken = decode(data.refresh);
                cookies.set(
                    "refresh",
                    data.refresh,
                    {
                        expires: new Date(decodedRefresh.exp * 1000),
                        path: "/"
                    });
            })
            .catch(() => {
                cookies.remove("refresh", {path: "/"});
            });
    }
};

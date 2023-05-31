import {AxiosInstance, AxiosRequestConfig} from "axios";
import Auth from "./Auth";
import Cookies from "universal-cookie";
import routes from "@root/Routes/Routes";

const cookies = new Cookies();

let refreshTokenRequest: Promise<void> | null = null;

export async function requestValidAccessToken() {
    // сначала запоминаем текущий accessToken из хранилища
    const accessToken = cookies.get("access_token");
    const refreshToken = cookies.get("refresh_token");
    if (
        refreshToken === undefined &&
        window.location.pathname !== routes.auth.login &&
        window.location.pathname !== routes.auth.registration
    ) {
        
        cookies.remove("access_token", {path: "/"});
        cookies.remove("refresh_token", {path: "/"});
        // обнуляем сторы
        window.location.href = routes.auth.login;
    }
    if (accessToken === undefined && refreshToken !== undefined) {

        if (refreshTokenRequest === null) {
            refreshTokenRequest = Auth.refresh(refreshToken);
        }
  
        await refreshTokenRequest;
  
        if (!refreshTokenRequest){
            refreshTokenRequest = null;
        }
    }
    
}
export const setAuthHeaderInterceptor = async (config: AxiosRequestConfig) => {
    const refreshToken = cookies.get("refresh_token");
    const currentUrl = `/v1/users/token-refresh?refresh_token=${refreshToken}`;
    if (config.url === currentUrl) return config;
    await requestValidAccessToken();
    const accessToken = cookies.get("access_token");
    if (accessToken && !config.headers.Authorization) {
        config.headers.Authorization = `Bearer ${accessToken}`;
    } else {
        delete config.headers.Authorization;
    }
    return config;
};

export const errorResponse = (error: any, axiosInstance: AxiosInstance) => {
    return Promise.reject(error);
};

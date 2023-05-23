import {AxiosInstance, AxiosRequestConfig} from "axios";
import Auth from "./Auth";
import Cookies from "universal-cookie";

const cookies = new Cookies();

export const setAuthHeaderInterceptor = (config: AxiosRequestConfig) => {
    const accessToken = cookies.get("access_token");
    if (accessToken) {
        config.headers.Authorization = `Bearer ${accessToken}`;
    } else {
        delete config.headers.Authorization;
    }
    return config;
};

export const refreshToken = (error: any, axiosInstance: AxiosInstance) => {
    const originalRequest = error.config;
    if (error.response && error.response.status === 401 && !originalRequest.retry) {
        originalRequest.retry = true;
        const refreshToken = cookies.get("refresh_token");
        if (refreshToken) {
            return Auth
                .refresh(refreshToken)
                .then(() => {
                    originalRequest.headers.Authorization = `Bearer ${refreshToken}`;
                    return axiosInstance(originalRequest);
                });
        }
    }
    return Promise.reject(error);
};

import Axios, {AxiosRequestConfig} from "axios";
import Qs from "qs";
import {setAuthHeaderInterceptor, refreshToken} from "./AuthApi/AuthInterceptors";

const localAxios = Axios.create({
    baseURL: "/api",
    paramsSerializer: (params) => Qs.stringify(params, {arrayFormat: "repeat"})
});

//Проставление заголовка с токеном
localAxios.interceptors.request.use(setAuthHeaderInterceptor);
//Обновление токена если вернулась 401
localAxios.interceptors.response.use((response) => response, (error) => refreshToken(error, localAxios));

export default {
    post: <T>(url: string, data?: any) => {
        return localAxios
            .post<T>(url, data);
    },
    get: <T>(url: string, params?: any, config?: AxiosRequestConfig) => {
        return localAxios
            .get<T>(
                url, 
                {
                    params,
                    ...config
                }
            );
    },
    put: <T>(url: string, params?: any) => {
        return localAxios
            .put<T>(
                url, 
                params
            );
    },
    delete: <T>(url: string, params?: any, config?: AxiosRequestConfig) => {
        return localAxios
            .delete<T>(
                url, 
                {
                    params,
                    ...config
                }
            );
    },
    patch: <T>(url: string, params?: any) => {
        return localAxios
            .patch<T>(
                url, 
                params
            );
    },
};

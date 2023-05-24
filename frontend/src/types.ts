import {AxiosResponse} from "axios";
import {CallEffect} from "redux-saga/effects";

export type children = string | null | JSX.Element;
export type UnboxPromise<T extends Promise<any>> = T extends Promise<infer U> ? U : never;
export type UnboxAxios<T extends AxiosResponse<any>> = T extends AxiosResponse<infer U> ? U : never;
type GenType<T> = Generator<CallEffect<AxiosResponse<T>>>;
export type UnboxCall<T extends GenType<any>> = T extends GenType<infer U> ? U : never;

export const Guard = {
    User: {
        isAuthUserInfo: (info: iApi.User.iUserInfo | null): info is iApi.User.iAuthUserInfo =>
            !!(info && "username" in info),
    },
};

export declare namespace iApi {
    namespace User {
        type iAuthUserInfo = {
            name: string;
            email: string;
            auth: boolean;
            id: string;
            created_at: string;
            updated_at: string;
        };
        type iUnauthUserInfo = {
            auth: boolean;
        };
        type iUserInfo = iUnauthUserInfo | iAuthUserInfo;
    }  
    namespace Error {
        type Item = {
            detail: {
                error: string,
                error_meta?: {
                      field: string
                }
            }[]
        }
    }
}

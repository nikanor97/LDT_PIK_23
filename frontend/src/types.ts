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
            !!(info && "name" in info),
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

    namespace Users {
        type Item = {
            id: string,
            name: string
        }
    }

    namespace Projects {
        // TODO Изменить в соответствии с беком
        type Item = {
            id: number,
            name: string,
            bathroomType: string,
            author: string,
            status: 100 | 200 | 400 | 300,
            performer: string,
            type: "dxf" | "manual"
        }
        type ItemDetail = Item & {
            resultOptions?: Result[]
        }

        type Result = {
            materials: {
                tabName: "Материалы",
                tables: {
                    name: string,
                    values: {
                        id: number,
                        name: string,
                        diameter1: number,
                        diameter2: number,
                        diameter3: number,
                        angle: number,
                        direction: string
                    }[]
                }[]
            },
            connectionPoints: {
                tabName: "Точки подключения",
                table: {
                    id: number,
                    order: string,
                    type: string,
                    diameter: number,
                    X: number,
                    Y: number,
                    Z: number,
                }[],
                image: string
            },
            graph: {
                tabName: "Граф подключения фитингов",
                table: {
                    id: number,
                    graph: string,
                    material: string,
                    probability: number,
                }[],
                image: string
            },
        }

        type DXFParsedData = {
            type: string,
            config: {
                title: string,
                value: string,
                x: number,
                y: number,
            }[]
        }

        type FittingGroup = {
            groupname: string,
            values: {
                image: string,
                name: string,
                id: string
            }[]
        }
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

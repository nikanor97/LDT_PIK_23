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
    namespace Statistic {
        type Item = {
            avg_n_fittings: number,
            avg_sewer_length: number,
            devices: {
                type_human: string,
                n_occur: number
            }[]
        };
    }

    namespace Projects {
        // TODO Изменить в соответствии с беком
        type Item = {
            id: string,
            name: string,
            bathroom_type: string,
            author_name: string,
            status: 0 | 100 | 200 | 400 | 300,
            worker_name: string,
            type: "dxf" | "manual",
            created_at: string
        }
        type ItemDetail = Item & {
            results?: Results[]
        }

        type Results = {
            n_fittings: number;
            sewer_length: number;
            variant_num: number;
            result: Result;
        }

        type Result = {
            fittings_stat: {
                tab_name: "Используемые фитинги",
                table: {
                    name: string,
                    material_id: string,
                    n_items: number,
                    total_length: number,
                }[],
                image: string
            },
            connection_points: {
                tab_name: "Точки подключения",
                table: {
                    id: number,
                    order: string,
                    type: string,
                    diameter: number,
                    coord_x: number,
                    coord_y: number,
                    coord_z: number,
                }[],
                image: string
            },
            graph: {
                tab_name: "Граф подключения фитингов",
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
            id: string,
            image: string,
            devices: {
                name: string,
                type: string,
                type_human: string,
                id: string,
                coord_x: number,
                coord_y: number,
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

import CommonLayout from "./CommonLayout/CommonLayout";
import {children} from "@types";

export type iLayoutProps = {
    children: children | children[];
    layoutClassname?: string;
    contentClassname?: string;
    headerClassname?: string;
}

export default {
    CommonLayout,
};


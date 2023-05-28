import CommonLayout from "./CommonLayout/CommonLayout";
import LkLayout from "./LkLayout/LkLayout";
import {children} from "@types";

export type iLayoutProps = {
    children: children | children[];
    layoutClassname?: string;
    contentClassname?: string;
    headerClassname?: string;
}

export default {
    CommonLayout,
    LkLayout
};


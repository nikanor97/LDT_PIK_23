// eslint-disable-next-line no-restricted-imports
import {useSelector, TypedUseSelectorHook} from "react-redux";
import {AppState} from "@root/Redux/store";

const useAppSelector: TypedUseSelectorHook<AppState> = useSelector;

export default useAppSelector;

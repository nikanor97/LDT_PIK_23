// eslint-disable-next-line no-restricted-imports
import {useDispatch} from "react-redux";
import type {AppDispatch} from "@root/Redux/store";

type DispatchFunc = () => AppDispatch
const useAppDispatch: DispatchFunc = useDispatch;

export default useAppDispatch;

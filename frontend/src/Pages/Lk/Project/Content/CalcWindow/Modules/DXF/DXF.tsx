import React, {useEffect, useState} from "react";
import styles from "./DXF.module.less";
import Title from "@root/Components/Title/Title";
import {Form, Input, Upload, InputNumber, Image} from "antd";
import {Button, FormItem} from "@root/Components/Controls";
import {UploadOutlined} from "@ant-design/icons";
import {RcFile} from "antd/lib/upload";
import {useAppDispatch, useAppSelector, useNotification} from "@root/Hooks";
import Actions from "@actions";
import {useParams} from "react-router-dom";
import Loading from "@root/Components/Loading/Loading";
import ErrorView from "@root/Components/Error/Error";
import transformData from "./Utils/TransformData";
import Hint from "@root/Components/Hint/Hint";

const {Dragger} = Upload;

type iParams = {
    projectID: string
}

const DXF = () => {
    const [file, setFile] = useState<RcFile[]>([]);
    const dispatch = useAppDispatch();
    const notification = useNotification();
    const {projectID} = useParams<iParams>();
    const parseDXFStatus = useAppSelector((state) => state.Projects.parseDXFStatus);
    const DXFData = useAppSelector((state) => state.Projects.DXFdata);
    const startCalcStatus = useAppSelector((state) => state.Projects.startCalcStatus);
    const [form] = Form.useForm();

    const beforeUpload = (file: RcFile, fileList: RcFile[]) => {
        if (fileList[0].name.split(".").pop() === "dxf") {
            setFile([fileList[0]]);
            if (fileList[0]) {
                dispatch(Actions.Projects.parseDXF({
                    dxf: fileList[0],
                    project_id: projectID
                }));
            }
        } else {
            notification({
                type: "error",
                message: "Неверный формат документа, загружать можно только dxf"
            });
        }
        return false;
    };

    const onFinish = () => {
        const formData = form.getFieldsValue();
        if (!DXFData) return null;
        const data = transformData({
            project_id: projectID,
            dxf_file_id: DXFData.id,
            ...formData
        });
        dispatch(Actions.Projects.startCalc(data));
    };

    useEffect(() => {
        return () => {
            dispatch(Actions.Projects.eraseDXFData());
            setFile([]);
        };
    }, []);

    const hint: React.ReactElement = (
        <div>
            <div className={styles.hintTitle}>Требования к загрузке:</div>
            <ul className={styles.hintText}>
                <li>приборы должны находиться в слое P-SANR-FIXT</li>
                <li>стояк должен быть в слое A-DETL</li>
                <li>стены должны быть заштрихованной областью в слое I-WALL-3</li>
            </ul>
        </div>
    ); 

    return (
        <div className={styles.wrapper}>
            <Title variant="h3" className={styles.title}>
                <div className={styles.titleText}>
                    <p>Загрузите DXF-файл</p>
                    <Hint title={hint}/>
                </div>

            </Title>
            <div className={styles.description}>
                Мы распознаем часть данных из DXF-файла. Некоторые поля необходимо будет заполнить самостоятельно.
            </div>
            <div className={styles.draggerImage}>
                <Dragger
                    accept=".dxf"
                    className={styles.dragger}
                    maxCount={1}
                    disabled={parseDXFStatus === "loading"}
                    multiple={false}
                    fileList={file && file}
                    onRemove={(file) => {
                        setFile([]);
                        dispatch(Actions.Projects.eraseDXFData());
                    }}
                    beforeUpload={beforeUpload}>
                    <p className={styles.draggerDesc}>Нажмите или перетяните файл</p>

                </Dragger>
                {parseDXFStatus === "success" && DXFData && (
                    <Image
                        className={styles.image}
                        src={`data:image/png;base64,${DXFData.image}`}
                    />
                )}
            </div>

            <div>
                {parseDXFStatus === "loading" && (
                    <div className={styles.loading}>
                        <Loading>
                            Загружаются данные из DXF файла,<br />
                            пожалуйста подождите...
                        </Loading>
                    </div>
                )}
                {parseDXFStatus === "success" && (
                    <div>
                        {DXFData && (
                            <Form form={form} onFinish={onFinish} className={styles.form}>
                                {/* <Title variant="h3" className={styles.formTitle}>
                                    Конфигурация
                                </Title>
                                <FormItem>
                                    <Input value={DXFData.type} disabled/>
                                </FormItem> */}
                                {DXFData.devices.map((item, index) => (
                                    <div key={index}>
                                        <Title variant="h3" className={styles.configTitle}>
                                            {item.type_human}
                                        </Title>
                                        <div className={styles.inputs}>
                                            <FormItem name={`${item.type}/${item.id}/${item.name}/X`} initialValue={item.coord_x} label={"X"}>
                                                <InputNumber
                                                    required
                                                    controls={false}
                                                    disabled/>
                                            </FormItem>
                                            <FormItem name={`${item.type}/${item.id}/${item.name}/Y`} initialValue={item.coord_y} label={"Y"}>
                                                <InputNumber
                                                    required
                                                    controls={false}
                                                    disabled/>
                                            </FormItem>
                                            <FormItem name={`${item.type}/${item.id}/${item.name}/Z`} label={"Z"} required>
                                                <InputNumber required controls={false}/>
                                            </FormItem>
                                        </div>

                                    </div>

                                ))}
                                <div className={styles.button}>
                                    <Button
                                        type="primary"
                                        htmlType="submit"
                                        loading={startCalcStatus === "loading"}
                                        disabled={startCalcStatus === "loading"}>
                                        Рассчитать
                                    </Button>
                                </div>

                            </Form>
                        )}
                    </div>
                )}
                {parseDXFStatus === "error" && (
                    <ErrorView>
                        При извлечении данных из DXF-файла произошла ошибка
                    </ErrorView>
                )}
            </div>
        </div>
    );
};

export default DXF;

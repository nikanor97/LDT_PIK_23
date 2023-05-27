import React, {useState} from "react";
import styles from "./DXF.module.less";
import Title from "@root/Components/Title/Title";
import {Form, Input, Upload, InputNumber} from "antd";
import {Button, FormItem} from "@root/Components/Controls";
import {UploadOutlined} from "@ant-design/icons";
import {RcFile} from "antd/lib/upload";
import {useAppDispatch, useAppSelector, useNotification} from "@root/Hooks";
import Actions from "@actions";
import {useParams} from "react-router-dom";
import Loading from "@root/Components/Loading/Loading";
import ErrorView from "@root/Components/Error/Error";
import transformData from "./Utils/TransformData";

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
                    project: Number(projectID)
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
        const data = transformData({
            project: Number(projectID),
            ...formData
        });
        dispatch(Actions.Projects.startCalc(data));
    };
    return (
        <div className={styles.wrapper}>
            <Title variant="h3" className={styles.title}>
                Загрузите DXF-файл
            </Title>
            <div className={styles.description}>
                Загрузите файл DXF, из него буду извлечены данные и после вам необходимо будет вписать еще некоторые данные и сделать запуск
            </div>
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
                <p className={styles.draggerDesc}>Нажмите или перетяните в эту область файл</p>
            </Dragger>
            <div>
                {parseDXFStatus === "loading" && (
                    <Loading />
                )}
                {parseDXFStatus === "success" && (
                    <div>
                        {DXFData && (
                            <Form form={form} onFinish={onFinish}>
                                <Title variant="h3" className={styles.formTitle}>
                                    Конфигурация
                                </Title>
                                <FormItem>
                                    <Input value={DXFData.type} disabled/>
                                </FormItem>
                                {DXFData.config.map((item, index) => (
                                    <div key={index}>
                                        <Title variant="h3" className={styles.configTitle}>
                                            {item.title} 
                                        </Title>
                                        <div className={styles.inputs}>
                                            <FormItem name={`${item.value}X`} initialValue={item.x} label={"X"}>
                                                <InputNumber
                                                    required
                                                    controls={false}
                                                    disabled/>
                                            </FormItem>
                                            <FormItem name={`${item.value}Y`} initialValue={item.y} label={"Y"}>
                                                <InputNumber
                                                    required
                                                    controls={false}
                                                    disabled/>
                                            </FormItem>
                                            <FormItem name={`${item.value}Z`} label={"Z"}>
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

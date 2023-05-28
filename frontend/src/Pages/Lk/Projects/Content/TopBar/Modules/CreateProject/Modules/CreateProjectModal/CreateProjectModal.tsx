import Actions from "@actions";
import React from "react";
import {Modal} from "@root/Components/Controls";
import {useAppDispatch, useAppSelector} from "@root/Hooks";
import CloseIcon from "@assets/Icons/Close/Close";
import {Checkbox, Form, Radio, Image} from "antd";
import {Input, Button, FormItem, Select} from "@components/Controls";
import styles from "./CreateProjectModal.module.less";
import GridContainer from "@root/Components/GridContainer/GridContainer";
import Title from "@root/Components/Title/Title";
const {Option} = Select;

const CreateProjectModal = () => {
    const showModal = useAppSelector((state) => state.Projects.createModal);
    const fittings = useAppSelector((state) => state.Projects.fittingsGroups);
    const users = useAppSelector((state) => state.User.users);
    const dispatch = useAppDispatch();
    const [form] = Form.useForm();

    if (!users) return null;
    if (!fittings) return null;

    const onSuccess = () => {
        form.resetFields();
    };

    const onCreate = () => {
        const fittingsNames = fittings.map((item) => item.groupname);

        const data = {
            worker_id: form.getFieldValue("worker_id"),
            fittings: fittingsNames
                .map((item) => form.getFieldValue(item))
                .flat()
                .filter((item) => item !== undefined && item !== null),
            type: "dxf",
            name: form.getFieldValue("name"),
            onSuccess
        };
        dispatch(Actions.Projects.createProject(data));
    };

    const setCreateModal = (mode: boolean) => {
        dispatch(Actions.Projects.setCreateModal(mode));
    };

    const onCloseModal = () => {
        setCreateModal(false);
    };

    return (
        <Modal
            antProps={{
                visible: showModal,
                title: "Создать проект",
                footer:
                        <Button
                            size="large"
                            type="primary"
                            htmlType="submit"
                            onClick={onCreate}
                            form="createProjectForm"
                            className={styles.button}>
                            Создать проект
                        </Button>,
                onCancel: onCloseModal,
                width: 640,
                className: styles.modal,
                closeIcon: <CloseIcon />,
                centered: true
            }}>
            
            <GridContainer className={styles.grid}>
                
                <Form
                    name="createProjectForm"
                    layout="vertical"
                    form={form}
                    id="createForm"
                    className={styles.form}
                    requiredMark={false}>
                    {/* <FormItem
                        name="type"
                        className={styles.formItem}
                        initialValue={"DXF"}
                        label="Способ построения маршрута">

                        <Radio.Group
                            buttonStyle="solid">
                            <Radio.Button value={"DXF"}>
                            DXF-файл
                            </Radio.Button>
                            <Radio.Button value={"manual"}>
                            Ручной ввод
                            </Radio.Button>
                        </Radio.Group>
                    </FormItem> */}
                    <FormItem
                        name="name"
                        className={styles.formItem}
                        rules={[
                            {
                                required: true,
                                message: "Поле не может быть пустым",
                            },
                        ]}
                        label="Название проекта">
                        <Input
                            placeholder={"Введите название"}
                            allowClear
                        />
                    </FormItem>
                    <FormItem
                        name="worker_id"
                        className={styles.formItem}
                        rules={[
                            {
                                required: true,
                                message: "Поле не может быть пустым",
                            },
                        ]}
                        label="Исполнитель проекта">
                        <Select
                            showArrow
                            showSearch={false}
                            placeholder="Выберете исполнителя"
                            maxTagCount="responsive"
                            className={styles.select}>
                            {users.map((user) => (
                                <Option
                                    key={user.id}
                                    value={user.id}>
                                    {user.name}
                                </Option>
                            ))}
                        </Select>
                    </FormItem>
                    <Title variant="h2" className={styles.fittingsTitle}>
                        Фитинги
                    </Title>
                    <Title variant="h3" className={styles.fittingsSubTitle}>
                        Выберите необходимые фитинги
                    </Title>
                    {fittings.map((item) => (
                        <FormItem
                            name={item.groupname}
                            key={item.groupname}
                            className={styles.formItem}>
                            <Checkbox.Group  className={styles.checkboxGroup}>
                                <Title variant="h2" className={styles.checkboxGroupTitle}>
                                    {item.groupname}
                                </Title>
                                {item.values.map((item) => (
                                    <div key={item.id} className={styles.checkboxWrapper}>
                                        
                                        <Checkbox key={item.id} value={item.id} />
                                        <Image src={`data:image/png;base64,${item.image}`} width={40} height={40} className={styles.checkboxImage} alt="fit"/>
                                        <div className={styles.checkboxChildren} >
                                            {item.name}
                                        </div>
                                        
                                    </div>

                                ))}
                            </Checkbox.Group>
                        </FormItem>

                    ))}
                </Form>
                
            </GridContainer>
            
        </Modal>
    );
};

export default CreateProjectModal;

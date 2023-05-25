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
import base64 from "./base64";
import Scrollbars from "react-custom-scrollbars";
const {Option} = Select;

const CreateProjectModal = () => {
    const showModal = useAppSelector((state) => state.Projects.createModal);
    const dispatch = useAppDispatch();
    const [form] = Form.useForm();

    //Mock

    const users = [
        {
            user_id: 1,
            username: "Пупкин В.С."
        },
        {
            user_id: 2,
            username: "Лупкин Г.В."
        }
    ];

    const fitings = [
        {
            groupName: "Тройники",
            values: [
                {
                    image: base64,
                    name: "Тройник 50х50х45",
                    id: 1
                },
                {
                    image: base64,
                    name: "Тройник 50х50х87",
                    id: 2
                },
                {
                    image: base64,
                    name: "Тройник 110х50х87",
                    id: 3
                },
            ]
        },
        {
            groupName: "Крестовины",
            values: [
                {
                    image: base64,
                    name: "Крестовина 50х50х45",
                    id: 4
                },
                {
                    image: base64,
                    name: "Крестовина 50х50х87",
                    id: 5
                },
                {
                    image: base64,
                    name: "Крестовина 110х50х87",
                    id: 6
                },
            ]
        }
    ];

    const onCreate = () => {
        const fitingsNames = fitings.map((item) => item.groupName);

        const data = {
            performer: form.getFieldValue("performer"),
            fitings: fitingsNames.map((item) => form.getFieldValue(item)).flat(),
            type: form.getFieldValue("type"),
            title: form.getFieldValue("title")
        };
        console.log(data);
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
                    <FormItem
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
                    </FormItem>
                    <FormItem
                        name="title"
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
                        name="performer"
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
                                    key={user.user_id}
                                    value={user.user_id}>
                                    {user.username}
                                </Option>
                            ))}
                        </Select>
                    </FormItem>
                    <Title variant="h2" className={styles.fitingsTitle}>
                        Фитинги
                    </Title>
                    <Title variant="h3" className={styles.fitingsSubTitle}>
                        Выберите необходимые фитинги
                    </Title>
                    {fitings.map((item) => (
                        <FormItem
                            name={item.groupName}
                            key={item.groupName}
                            className={styles.formItem}>

                            <Checkbox.Group  className={styles.checkboxGroup}>
                                <Title variant="h2" className={styles.checkboxGroupTitle}>
                                    {item.groupName}
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

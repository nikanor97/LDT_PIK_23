import Actions from "@actions";
import React, {useState} from "react";
import {Modal} from "@root/Components/Controls";
import {useAppDispatch, useAppSelector, useNotification} from "@root/Hooks";
import CloseIcon from "@assets/Icons/Close/Close";
import {Checkbox, Form, Radio, Image} from "antd";
import {Input, Button, FormItem, Select} from "@components/Controls";
import styles from "./CreateProjectModal.module.less";
import GridContainer from "@root/Components/GridContainer/GridContainer";
import Title from "@root/Components/Title/Title";
import {CheckboxChangeEvent} from "antd/lib/checkbox";
const {Option} = Select;

const CreateProjectModal = () => {
    const showModal = useAppSelector((state) => state.Projects.createModal);
    const fittings = useAppSelector((state) => state.Projects.fittingsGroups);
    const users = useAppSelector((state) => state.User.users);
    const dispatch = useAppDispatch();
    const [form] = Form.useForm();
    const [selectedIds, setSelectedIds] = useState<string[]>([]);
    const notification = useNotification();

    if (!users) return null;
    if (!fittings) return null;

    const allIds = fittings.flatMap((group) => group.values.map((value) => value.id));

    const handleCheckboxChange = (id: string) => {
        const selectedIndex = selectedIds.indexOf(id);
        let updatedSelectedIds: string[];
    
        if (selectedIndex === -1) {
            // Add the ID to the selected IDs array
            updatedSelectedIds = [...selectedIds, id];
        } else {
            // Remove the ID from the selected IDs array
            updatedSelectedIds = [
                ...selectedIds.slice(0, selectedIndex),
                ...selectedIds.slice(selectedIndex + 1),
            ];
        }
    
        setSelectedIds(updatedSelectedIds);
    };
    
    const handleSelectAllChange = (event: CheckboxChangeEvent) => {
    
        setSelectedIds(event.target.checked ? allIds : []);
    };

    const onSuccess = () => {
        form.resetFields();
    };

    const onCreate = () => {

        if (!form.getFieldValue("worker_id")) {
            form.setFields([
                {
                    name: "worker_id",
                    errors: ["Поле не может быть пустым"]
                },
            ]);
        }

        if (!form.getFieldValue("name")) {
            form.setFields([
                {
                    name: "name",
                    errors: ["Поле не может быть пустым"]
                },
            ]);
        }

        if (!form.getFieldValue("worker_id") || !form.getFieldValue("name")) {
            notification({
                type: "error",
                message: "Поля название и исполнитель обязательные"
            });
            return null;
        }

        if (selectedIds.length === 0) {
            notification({
                type: "error",
                message: "Необходимо выбрать фитинги"
            });
            return null;
        }

        const data = {
            worker_id: form.getFieldValue("worker_id"),
            fittings_ids: selectedIds,
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
                    <div>
                        <div  className={styles.checkboxWrapper}>
                            <Checkbox
                                onChange={handleSelectAllChange}
                                indeterminate={selectedIds.length > 0 && selectedIds.length < allIds.length}
                                checked={selectedIds.length === allIds.length}>
                                Выбрать все
                            </Checkbox>
                        </div>
                        {fittings.map((group) => (
                            <div key={group.groupname}>
                                <Title variant="h2" className={styles.checkboxGroupTitle}>
                                    {group.groupname}
                                </Title>
                                {group.values.map((item) => (
                                    <div key={item.id} className={styles.checkboxWrapper}>
                                        <Checkbox
                                            key={item.id}
                                            value={item.id}
                                            checked={selectedIds.includes(item.id)}
                                            onChange={() => handleCheckboxChange(item.id)}/>
                                        <Image src={`data:image/png;base64,${item.image}`} width={40} height={40} className={styles.checkboxImage} alt="fit"/>
                                        <div className={styles.checkboxChildren} >
                                            {item.name}
                                        </div>
                                                                        
                                    </div>
                                ))}
                            </div>
                        ))}
                    </div>
                    {/* {fittings.map((item) => (
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

                    ))} */}
                </Form>
                
            </GridContainer>
            
        </Modal>
    );
};

export default CreateProjectModal;

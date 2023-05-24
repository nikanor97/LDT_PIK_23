import React from "react";
import styles from "./Registration.module.less";
import {Form} from "antd";
import {Input, Button, FormItem, Checkbox} from "@components/Controls";
import Actions from "@actions";
import {useAppDispatch, useAppSelector} from "@root/Hooks";
import {Auth} from "@root/Api/AuthApi/types";
import Navigation from "../../Modules/Navigation/Navigation";
import routes from "@routes";
import Title from "@root/Components/Title/Title";
import {useHistory} from "react-router-dom";
import Logo from "../../Icons/Logo";
import {iApi} from "@types";

const Registration = () => {
    const [form] = Form.useForm();
    const dispatch = useAppDispatch();
    const history = useHistory();
    const state = useAppSelector((state) => state.Auth.registration);

    const setFieldsErrors = (errors: iApi.Error.Item) => {
        form.setFields(errors.detail.map((item) => (
            {
                name: item.error_meta!.field,
                errors: [item.error]
            }))
        );
    };

    const redirect = () => {
        history.push(routes.auth.login);
    };

    const onRegistration = (values: Auth.iRegistration) => {
        dispatch(Actions.Auth.userRegistration({
            ...values,
            setFieldsErrors,
            redirect
        }));
    };

    const onValuesChange = (values: Auth.iRegistration) => {
        Object.keys(values).forEach((field) => {
            const error = form.getFieldError(field);
            if (!error.length) {
                return;
            }
            // Clear error message of field
            form.setFields([
                {
                    name: field,
                    errors: []
                }
            ]);
        });
    };

    return (
        <>
            <div className={styles.logo}>
                <Logo />
            </div>
            <Title
                variant="h1" 
                className={styles.title}>
                Регистрация
            </Title>
            <Form
                form={form}
                name="register"
                onFinish={onRegistration}
                layout="vertical"
                scrollToFirstError
                onValuesChange={onValuesChange}
                className={styles.form}>
                <FormItem
                    name="name"
                    className={styles.item}
                    label="Имя пользователя"
                    required>
                    <Input
                        allowClear
                        className={styles.input}
                        placeholder="Введите ваше имя" 
                        disabled={state.fetching}
                    />
                </FormItem>
                <FormItem
                    name="email"
                    className={styles.item}
                    label="E-mail"
                    required
                    rules={[
                        {
                            type: "email",
                            message: "E-mail не подходит",
                        },
                    ]}>
                    <Input
                        allowClear
                        className={styles.input}
                        placeholder="Введите ваш email адрес" 
                        disabled={state.fetching}
                    />
                </FormItem>
                <FormItem
                    name="password"
                    className={styles.item}
                    label="Пароль"
                    required>
                    <Input.Password 
                        disabled={state.fetching}
                        className={styles.input}
                        placeholder="Введите пароль"
                    />
                </FormItem>
                <FormItem
                    name="confirm"
                    className={styles.item}
                    label="Подтверждение пароля"
                    dependencies={["password"]}
                    required
                    rules={[
                        ({getFieldValue}) => ({
                            validator(rule,value) {
                                if (!value || getFieldValue("password") === value) {
                                    return Promise.resolve();
                                }
                                return Promise.reject(new Error("Пароли не совпадают"));
                            },
                        }),
                    ]}>
                    <Input.Password 
                        disabled={state.fetching}
                        className={styles.input}
                        placeholder="Повторите пароль"
                    />
                </FormItem>
                <div className={styles.controls}>
                    <FormItem
                        className={styles.formItem}>
                        <Button
                            loading={state.fetching}
                            size="large"
                            type="primary"
                            className={styles.button}
                            htmlType="submit">
                            Зарегистрироваться
                        </Button>
                    </FormItem>
                    <FormItem
                        className={styles.formItem}>
                        <Button
                            className={styles.linkButton}
                            type="link">
                            <Navigation route={routes.auth.login}>
                                Уже зарегистрированы?
                            </Navigation>
                        </Button>
                    </FormItem>
                </div>
            </Form>
        </>

    );
};

export default Registration;

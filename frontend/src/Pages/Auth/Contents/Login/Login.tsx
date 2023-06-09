import React from "react";
import styles from "./Login.module.less";
import {Form} from "antd";
import Title from "@root/Components/Title/Title";
import {Button, FormItem, Input} from "@root/Components/Controls";
import Actions from "@actions";
import {useAppDispatch, useAppSelector} from "@root/Hooks";
import {Auth} from "@root/Api/AuthApi/types";
import Navigation from "../../Modules/Navigation/Navigation";
import routes from "@routes";
import {useHistory} from "react-router-dom";
import Logo from "../../../../Assets/Logo/Logo";
import {iApi} from "@types";

const Login = () => {
    const [form] = Form.useForm();
    const dispatch = useAppDispatch();
    const history = useHistory();
    const state = useAppSelector((state) => state.Auth.login);

    const setFieldsErrors = (errors: iApi.Error.Item) => {
        form.setFields(errors.detail.map((item) => (
            {
                name: item.error_meta!.field,
                errors: [item.error]
            }))
        );
    };

    const redirect = () => {
        history.push("/");
    };

    const onLogin = (values: Auth.iLogin) => {
        dispatch(Actions.Auth.userLogin({
            ...values,
            setFieldsErrors,
            redirect
        }));
    };

    const onValuesChange = (values: Auth.iLogin) => {
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
        <div className={styles.wrapper}>
            <div className={styles.logo}>
                <Logo />
            </div>
            <Title
                variant="h1" 
                className={styles.title}>
                Авторизация
            </Title>
            <Form
                form={form}
                name="Login"
                layout="vertical"
                onValuesChange={onValuesChange}
                onFinish={onLogin}>
                <FormItem
                    name="username"
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
                        disabled={state.fetching}
                        className={styles.input}
                        placeholder="E-mail" 
                    />
                </FormItem>
                <FormItem
                    name="password"
                    label="Пароль"
                    required>
                    <Input.Password
                        disabled={state.fetching}
                        type="password"
                        className={styles.input}
                        placeholder="Пароль"
                    />
                </FormItem>
                <div className={styles.controls}>
                    <FormItem
                        className={styles.formItem}>
                        <Button
                            size="large"
                            type="primary"
                            loading={state.fetching}
                            htmlType="submit"
                            className={styles.button}>
                            Войти
                        </Button>
                    </FormItem>
                    <FormItem
                        className={styles.formItem}>
                        <Button
                            className={styles.linkButton}
                            type="link">
                            <Navigation route={routes.auth.registration}>
                                Еще не зарегистрированы?
                            </Navigation>
                        </Button>
                    </FormItem>
                </div>
            </Form>
        </div>
        
    );
};

export default Login;

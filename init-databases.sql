-- Создание пользователей
CREATE USER auth_user WITH PASSWORD 'auth_password';

-- Создание баз данных и назначение владельцев
CREATE DATABASE auth_service_db OWNER auth_user;

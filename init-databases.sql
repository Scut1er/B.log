-- Создание пользователей
CREATE USER auth_user WITH PASSWORD 'auth_password';
CREATE USER team_user WITH PASSWORD 'team_password';

-- Создание баз данных и назначение владельцев
CREATE DATABASE auth_service_db OWNER auth_user;
CREATE DATABASE team_service_db OWNER team_user;

-- Criação do banco de dados
CREATE DATABASE IF NOT EXISTS wolfx_bd;

USE wolfx_bd;

grant all privileges on *.* to 'root'@'%' identified by 'root' with grant option;
FLUSH PRIVILEGES;
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(200),
    email VARCHAR(200),
    senha VARCHAR(200),
    nivel_acesso VARCHAR(200)
);
-- Conceda permissões ao usuário root para acessar de qualquer host
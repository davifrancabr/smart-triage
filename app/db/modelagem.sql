CREATE TABLE pacientes (
    cpf VARCHAR(11) PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    tipo_preferencial VARCHAR(50)
);

CREATE TABLE medicos (
    crm VARCHAR(12) PRIMARY KEY,
    nome VARCHAR(100) NOT NULL
);

CREATE TABLE triagens (
    id_atendimento INT AUTO_INCREMENT PRIMARY KEY,
    cpf_paciente VARCHAR(11) NOT NULL,
    crm_medico VARCHAR(12),
    sintomas_relatados TEXT NOT NULL,
    classificacao_risco ENUM('Vermelho', 'Amarelo', 'Verde') NOT NULL,
    status ENUM('Aguardando', 'Em Atendimento', 'Atendido', 'Cancelado') DEFAULT 'Aguardando',
    data_hora_chegada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (cpf_paciente) REFERENCES pacientes(cpf),
    FOREIGN KEY (crm_medico) REFERENCES medicos(crm)
);
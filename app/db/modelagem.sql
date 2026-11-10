-- Paciente
CREATE TABLE IF NOT EXISTS pacientes
(
    cpf               VARCHAR(11)       NOT NULL PRIMARY KEY,
    nome              VARCHAR(100)      NOT NULL,
    idade             SMALLINT UNSIGNED NOT NULL,
    tipo_preferencial VARCHAR(50)       NOT NULL DEFAULT 'Normal'
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

-- Medico
CREATE TABLE IF NOT EXISTS medicos
(
    crm           VARCHAR(12) PRIMARY KEY,
    nome          VARCHAR(100) NOT NULL,
    especialidade VARCHAR(80)  NOT NULL
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

-- Atendimento
CREATE TABLE IF NOT EXISTS triagens
(
    id_atendimento      INT AUTO_INCREMENT PRIMARY KEY,
    cpf_paciente        VARCHAR(11)                                                    NOT NULL,
    crm_medico          VARCHAR(12)                                                    NULL,
    observacao          TEXT                                                           NULL,
    sintomas_relatados  TEXT                                                           NOT NULL,
    classificacao_risco ENUM ('Vermelho', 'Amarelo', 'Verde')                          NOT NULL,
    status              ENUM ('Aguardando', 'Em Atendimento', 'Atendido', 'Cancelado') NOT NULL DEFAULT 'Aguardando',
    data_hora_chegada   TIMESTAMP                                                      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_triagem_status (status),
    INDEX idx_triagem_classRisco (classificacao_risco),

    FOREIGN KEY (cpf_paciente) REFERENCES pacientes (cpf),
    FOREIGN KEY (crm_medico) REFERENCES medicos (crm)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

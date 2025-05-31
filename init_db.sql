CREATE DATABASE FluxKart;

USE FluxKart;

CREATE TABLE Contact (
    id INT AUTO_INCREMENT PRIMARY KEY,
    phoneNumber VARCHAR(20),
    email VARCHAR(255),
    linkedId INT,
    linkPrecedence ENUM('primary', 'secondary') NOT NULL DEFAULT 'primary',
    createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deletedAt DATETIME DEFAULT NULL,
    FOREIGN KEY (linkedId) REFERENCES Contact(id)
);

INSERT INTO Contact (
    id, phoneNumber, email, linkedId, linkPrecedence, createdAt, updatedAt, deletedAt
) VALUES (
    1, '123456', 'lorraine@hillvalley.edu', NULL, 'primary',
    '2023-04-01 00:00:00.374', '2023-04-01 00:00:00.374', NULL
);

INSERT INTO Contact (
    id, phoneNumber, email, linkedId, linkPrecedence, createdAt, updatedAt, deletedAt
) VALUES (
    23, '123456', 'mcfly@hillvalley.edu', 1, 'secondary',
    '2023-04-20 05:30:00.110', '2023-04-20 05:30:00.110', NULL
);

SELECT * FROM contact;

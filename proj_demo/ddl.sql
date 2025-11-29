CREATE DATABASE IF NOT EXISTS prj_demo;
USE prj_demo;

CREATE TABLE accounts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100),
  balance DECIMAL(10,2)
);

CREATE TABLE account_audit (
  id INT AUTO_INCREMENT PRIMARY KEY,
  account_id INT,
  action VARCHAR(50),
  amount DECIMAL(10,2),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO accounts (name, balance) VALUES
('Doni', 200.00),
('Sinta', 150.00),
('Ryan', 300.00);

DELIMITER $$	# Script harus diekskusi menggunakan Delimiter $$
CREATE PROCEDURE sp_transfer(IN p_from INT, IN p_to INT, IN p_amount DECIMAL(10,2))
BEGIN
  START TRANSACTION;
    UPDATE accounts SET balance = balance - p_amount WHERE id = p_from;
    UPDATE accounts SET balance = balance + p_amount WHERE id = p_to;
  COMMIT;
END$$			# Akhiri Delimiter $$

DELIMITER $$	# Script harus diekskusi menggunakan Delimiter $$
CREATE FUNCTION fn_get_balance(p_id INT) RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
  DECLARE v_balance DECIMAL(10,2);
  SELECT balance INTO v_balance FROM accounts WHERE id = p_id;
  RETURN v_balance;
END$$			# Akhiri Delimiter $$


CREATE VIEW v_accounts_overview AS
SELECT id, name, balance FROM accounts;

DELIMITER $$	# Script harus diekskusi menggunakan Delimiter $$
CREATE TRIGGER trg_account_update AFTER UPDATE ON accounts
FOR EACH ROW
BEGIN
  INSERT INTO account_audit (account_id, action, amount)
  VALUES (NEW.id, 'update_balance', NEW.balance - OLD.balance);
END$$			# Akhiri Delimiter $$

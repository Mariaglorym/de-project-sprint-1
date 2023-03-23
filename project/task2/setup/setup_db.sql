
DROP VIEW IF EXISTS analysis.Orders;

ALTER TABLE production.Orders DROP COLUMN status;

CREATE VIEW analysis.Orders AS SELECT * FROM production.Orders;

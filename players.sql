BEGIN TRANSACTION;
CREATE TABLE "Players" (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`Name`	TEXT,
	`Last_Answered_Question`	TEXT
);
INSERT INTO `Players` VALUES (1,'Кирилл','0');
INSERT INTO `Players` VALUES (2,'Максим','2');
COMMIT;

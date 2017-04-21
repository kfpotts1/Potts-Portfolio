CREATE TABLE Salesperson (
    ID INTEGER,
    Name TEXT,
    Age INTEGER,
    Salary INTEGER);
    
CREATE TABLE Orders (
    Number INTEGER,
    order_date TEXT,
    cust_id INTEGER,
    salesperson_id INTEGER,
    Amount INTEGER);
    
    
INSERT INTO Salesperson(ID, Name, Age, Salary) VALUES (1, "Kyle", 61, 165000);
INSERT INTO Salesperson(ID, Name, Age, Salary) VALUES (2, "Kelsey", 34, 34000);
INSERT INTO Salesperson(ID, Name, Age, Salary) VALUES (5, "Cam", 34, 105000);
INSERT INTO Salesperson(ID, Name, Age, Salary) VALUES (7, "Paul", 41, 31000);
INSERT INTO Salesperson(ID, Name, Age, Salary) VALUES (8, "Charlie", 57, 63000);
INSERT INTO Salesperson(ID, Name, Age, Salary) VALUES (11, "Syd", 38, 92000);

INSERT INTO Orders(Number, order_date, cust_id, salesperson_id, Amount) VALUES(10, "1/2/94", 4, 2, 800);
INSERT INTO Orders(Number, order_date, cust_id, salesperson_id, Amount) VALUES (20, "1/30/98", 4, 8, 510);
INSERT INTO Orders(Number, order_date, cust_id, salesperson_id, Amount) VALUES (30, "7/14/91", 9, 1, 2160);
INSERT INTO Orders(Number, order_date, cust_id, salesperson_id, Amount) VALUES (40, "1/29/95", 7, 2, 600);
INSERT INTO Orders(Number, order_date, cust_id, salesperson_id, Amount) VALUES (50, "2/2/97", 6, 7, 820);
INSERT INTO Orders(Number, order_date, cust_id, salesperson_id, Amount) VALUES (60, "1/3/97", 6, 7, 520);
INSERT INTO Orders(Number, order_date, cust_id, salesperson_id, Amount) VALUES (70, "8/1/99", 9, 7, 350);

-- names of salespersons with more than 1 sale
SELECT Salesperson.name FROM Salesperson JOIN Orders ON Orders.salesperson_id = Salesperson.ID GROUP BY Salesperson.ID HAVING COUNT(*) > 1;

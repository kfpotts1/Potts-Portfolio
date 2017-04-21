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
    
    
INSERT INTO Salesperson(ID, Name, Age, Salary) VALUES (1, "Abe", 61, 140000);
INSERT INTO Salesperson(ID, Name, Age, Salary) VALUES (2, "Bob", 34, 44000);
INSERT INTO Salesperson(ID, Name, Age, Salary) VALUES (5, "Chris", 34, 40000);
INSERT INTO Salesperson(ID, Name, Age, Salary) VALUES (7, "Dan", 41, 52000);
INSERT INTO Salesperson(ID, Name, Age, Salary) VALUES (8, "Ken", 57, 115000);
INSERT INTO Salesperson(ID, Name, Age, Salary) VALUES (11, "Joe", 38, 38000);

INSERT INTO Orders(Number, order_date, cust_id, salesperson_id, Amount) VALUES(10, "8/2/96", 4, 2, 540);
INSERT INTO Orders(Number, order_date, cust_id, salesperson_id, Amount) VALUES (20, "1/30/99", 4, 8, 1800);
INSERT INTO Orders(Number, order_date, cust_id, salesperson_id, Amount) VALUES (30, "7/14/95", 9, 1, 460);
INSERT INTO Orders(Number, order_date, cust_id, salesperson_id, Amount) VALUES (40, "1/29/98", 7, 2, 2400);
INSERT INTO Orders(Number, order_date, cust_id, salesperson_id, Amount) VALUES (50, "2/3/98", 6, 7, 600);
INSERT INTO Orders(Number, order_date, cust_id, salesperson_id, Amount) VALUES (60, "3/2/98", 6, 7, 720);
INSERT INTO Orders(Number, order_date, cust_id, salesperson_id, Amount) VALUES (70, "5/6/98", 9, 7, 150);

-- names of salespersons with more than 1 sale
SELECT Salesperson.name FROM Salesperson JOIN Orders ON Orders.salesperson_id = Salesperson.ID GROUP BY Salesperson.ID HAVING COUNT(*) > 1;

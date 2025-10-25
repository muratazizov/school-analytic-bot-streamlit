-- Create Database

-- 1. Create the database if it doesn't exist
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'SchoolDB')
BEGIN
    CREATE DATABASE SchoolDB;
END
GO

-- 2. Create SQL Server Login
USE master;
GO

IF NOT EXISTS (SELECT * FROM sys.server_principals WHERE name = 'schooladmin')
BEGIN
    CREATE LOGIN schooladmin WITH PASSWORD = 'School@2024!';
END
GO

-- 3. Create Database User and grant permissions
USE SchoolDB;
GO

IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = 'schooladmin')
BEGIN
    CREATE USER schooladmin FOR LOGIN schooladmin;
END
GO

-- 4. Add user to db_owner role (full permissions)
ALTER ROLE db_owner ADD MEMBER schooladmin;
GO

-- Verify the user was created
SELECT name, type_desc FROM sys.database_principals WHERE name = 'schooladmin';
GO

USE SchoolDB;
GO
-- Drop existing tables
IF OBJECT_ID('dbo.Attendance', 'U') IS NOT NULL DROP TABLE dbo.Attendance;
IF OBJECT_ID('dbo.Scores', 'U') IS NOT NULL DROP TABLE dbo.Scores;
IF OBJECT_ID('dbo.LibraryCheckouts', 'U') IS NOT NULL DROP TABLE dbo.LibraryCheckouts;
IF OBJECT_ID('dbo.ClassEnrollments', 'U') IS NOT NULL DROP TABLE dbo.ClassEnrollments;
IF OBJECT_ID('dbo.Classes', 'U') IS NOT NULL DROP TABLE dbo.Classes;
IF OBJECT_ID('dbo.Books', 'U') IS NOT NULL DROP TABLE dbo.Books;
IF OBJECT_ID('dbo.Subjects', 'U') IS NOT NULL DROP TABLE dbo.Subjects;
IF OBJECT_ID('dbo.Teachers', 'U') IS NOT NULL DROP TABLE dbo.Teachers;
IF OBJECT_ID('dbo.Students', 'U') IS NOT NULL DROP TABLE dbo.Students;
GO

USE SchoolDB;
GO
-- Students Table
CREATE TABLE Students (
    StudentID INT PRIMARY KEY IDENTITY(1,1),
    FirstName NVARCHAR(50) NOT NULL,
    LastName NVARCHAR(50) NOT NULL,
    DateOfBirth DATE NOT NULL,
    Grade INT NOT NULL CHECK (Grade BETWEEN 1 AND 12),
    EnrollmentDate DATE NOT NULL,
    Email NVARCHAR(100),
    IsActive BIT DEFAULT 1
);

-- Teachers Table
CREATE TABLE Teachers (
    TeacherID INT PRIMARY KEY IDENTITY(1,1),
    FirstName NVARCHAR(50) NOT NULL,
    LastName NVARCHAR(50) NOT NULL,
    Email NVARCHAR(100) NOT NULL,
    HireDate DATE NOT NULL,
    Department NVARCHAR(50),
    IsActive BIT DEFAULT 1
);

-- Subjects Table
CREATE TABLE Subjects (
    SubjectID INT PRIMARY KEY IDENTITY(1,1),
    SubjectName NVARCHAR(100) NOT NULL,
    SubjectCode NVARCHAR(10) NOT NULL UNIQUE,
    Description NVARCHAR(500),
    CreditHours INT DEFAULT 1
);

-- Classes Table
CREATE TABLE Classes (
    ClassID INT PRIMARY KEY IDENTITY(1,1),
    SubjectID INT NOT NULL FOREIGN KEY REFERENCES Subjects(SubjectID),
    TeacherID INT NOT NULL FOREIGN KEY REFERENCES Teachers(TeacherID),
    Grade INT NOT NULL CHECK (Grade BETWEEN 1 AND 12),
    Section NVARCHAR(10),
    AcademicYear INT NOT NULL,
    Semester NVARCHAR(20) NOT NULL,
    RoomNumber NVARCHAR(20)
);

-- Class Enrollments Table
CREATE TABLE ClassEnrollments (
    EnrollmentID INT PRIMARY KEY IDENTITY(1,1),
    StudentID INT NOT NULL FOREIGN KEY REFERENCES Students(StudentID),
    ClassID INT NOT NULL FOREIGN KEY REFERENCES Classes(ClassID),
    EnrollmentDate DATE NOT NULL DEFAULT GETDATE()
);

-- Scores Table
CREATE TABLE Scores (
    ScoreID INT PRIMARY KEY IDENTITY(1,1),
    StudentID INT NOT NULL FOREIGN KEY REFERENCES Students(StudentID),
    ClassID INT NOT NULL FOREIGN KEY REFERENCES Classes(ClassID),
    Quarter INT NOT NULL CHECK (Quarter BETWEEN 1 AND 4),
    Score DECIMAL(5,2) NOT NULL CHECK (Score BETWEEN 0 AND 100),
    LetterGrade NVARCHAR(2),
    RecordedDate DATE NOT NULL DEFAULT GETDATE()
);

-- Attendance Table
CREATE TABLE Attendance (
    AttendanceID INT PRIMARY KEY IDENTITY(1,1),
    StudentID INT NOT NULL FOREIGN KEY REFERENCES Students(StudentID),
    ClassID INT NOT NULL FOREIGN KEY REFERENCES Classes(ClassID),
    AttendanceDate DATE NOT NULL,
    Status NVARCHAR(20) NOT NULL CHECK (Status IN ('Present', 'Absent', 'Tardy', 'Excused')),
    Notes NVARCHAR(500)
);

-- Books Table
CREATE TABLE Books (
    BookID INT PRIMARY KEY IDENTITY(1,1),
    ISBN NVARCHAR(20) UNIQUE,
    Title NVARCHAR(200) NOT NULL,
    Author NVARCHAR(100) NOT NULL,
    Publisher NVARCHAR(100),
    PublicationYear INT,
    Category NVARCHAR(50),
    TotalCopies INT NOT NULL DEFAULT 1,
    AvailableCopies INT NOT NULL DEFAULT 1
);

-- Library Checkouts Table
CREATE TABLE LibraryCheckouts (
    CheckoutID INT PRIMARY KEY IDENTITY(1,1),
    BookID INT NOT NULL FOREIGN KEY REFERENCES Books(BookID),
    StudentID INT NOT NULL FOREIGN KEY REFERENCES Students(StudentID),
    CheckoutDate DATE NOT NULL DEFAULT GETDATE(),
    DueDate DATE NOT NULL,
    ReturnDate DATE NULL,
    Status NVARCHAR(20) NOT NULL CHECK (Status IN ('Checked Out', 'Returned', 'Overdue'))
);

USE SchoolDB;
GO

-- Insert Sample Data

-- Students
INSERT INTO Students (FirstName, LastName, DateOfBirth, Grade, EnrollmentDate, Email) VALUES
('John', 'Adams', '2010-03-15', 9, '2023-09-01', 'john.adams@school.edu'),
('Emily', 'Johnson', '2009-07-22', 10, '2022-09-01', 'emily.johnson@school.edu'),
('Michael', 'Brown', '2011-11-08', 8, '2023-09-01', 'michael.brown@school.edu'),
('Sarah', 'Davis', '2010-05-30', 9, '2023-09-01', 'sarah.davis@school.edu'),
('David', 'Wilson', '2008-09-12', 11, '2021-09-01', 'david.wilson@school.edu'),
('Jessica', 'Martinez', '2012-01-25', 7, '2023-09-01', 'jessica.martinez@school.edu'),
('Daniel', 'Garcia', '2009-04-18', 10, '2022-09-01', 'daniel.garcia@school.edu'),
('Ashley', 'Rodriguez', '2011-08-03', 8, '2023-09-01', 'ashley.rodriguez@school.edu');

-- Teachers
INSERT INTO Teachers (FirstName, LastName, Email, HireDate, Department) VALUES
('Robert', 'Thompson', 'r.thompson@school.edu', '2015-08-15', 'Mathematics'),
('Linda', 'Anderson', 'l.anderson@school.edu', '2012-08-20', 'English'),
('James', 'Taylor', 'j.taylor@school.edu', '2018-08-18', 'Science'),
('Patricia', 'Moore', 'p.moore@school.edu', '2010-08-22', 'History');

-- Subjects
INSERT INTO Subjects (SubjectName, SubjectCode, Description, CreditHours) VALUES
('Algebra I', 'MATH101', 'Introduction to algebra', 1),
('Geometry', 'MATH102', 'Study of shapes and spatial relationships', 1),
('English Literature', 'ENG101', 'Literature analysis and composition', 1),
('Biology', 'SCI101', 'Study of living organisms', 1),
('US History', 'HIST101', 'American history from colonial times to present', 1);

-- Classes
INSERT INTO Classes (SubjectID, TeacherID, Grade, Section, AcademicYear, Semester, RoomNumber) VALUES
(1, 1, 9, 'A', 2024, 'Fall', '201'),
(2, 1, 10, 'B', 2024, 'Fall', '202'),
(3, 2, 9, 'A', 2024, 'Fall', '105'),
(4, 3, 9, 'A', 2024, 'Fall', '301'),
(5, 4, 9, 'A', 2024, 'Fall', '108');

-- Class Enrollments
INSERT INTO ClassEnrollments (StudentID, ClassID) VALUES
(1, 1), (1, 3), (1, 4), (1, 5),
(2, 2), (2, 3),
(3, 1), (3, 4),
(4, 1), (4, 3),
(5, 2), (5, 3);

-- Scores
INSERT INTO Scores (StudentID, ClassID, Quarter, Score, LetterGrade) VALUES
-- John Adams scores
(1, 1, 1, 85.5, 'B'),
(1, 1, 2, 88.0, 'B+'),
(1, 1, 3, 92.5, 'A-'),
(1, 3, 1, 90.0, 'A-'),
(1, 3, 2, 87.5, 'B+'),
(1, 4, 1, 88.0, 'B+'),
-- Emily Johnson scores
(2, 2, 1, 95.0, 'A'),
(2, 2, 2, 93.5, 'A'),
(2, 3, 1, 91.0, 'A-'),
-- Michael Brown scores
(3, 1, 1, 78.0, 'C+'),
(3, 1, 2, 82.0, 'B-'),
(3, 4, 1, 85.0, 'B'),
-- Sarah Davis scores
(4, 1, 1, 92.0, 'A-'),
(4, 3, 1, 89.0, 'B+');

-- Books
INSERT INTO Books (ISBN, Title, Author, Category, TotalCopies, AvailableCopies) VALUES
('978-0-14-028329-3', 'To Kill a Mockingbird', 'Harper Lee', 'Fiction', 5, 3),
('978-0-545-01022-1', 'The Hunger Games', 'Suzanne Collins', 'Young Adult', 8, 5),
('978-0-439-13959-5', 'Harry Potter and the Goblet of Fire', 'J.K. Rowling', 'Fantasy', 10, 7),
('978-0-06-112008-4', 'The Great Gatsby', 'F. Scott Fitzgerald', 'Fiction', 6, 4),
('978-0-7432-7356-5', '1984', 'George Orwell', 'Fiction', 7, 5),
('978-0-316-76948-0', 'The Catcher in the Rye', 'J.D. Salinger', 'Fiction', 4, 2);

-- Library Checkouts
INSERT INTO LibraryCheckouts (BookID, StudentID, CheckoutDate, DueDate, ReturnDate, Status) VALUES
(1, 1, '2024-09-15', '2024-10-15', '2024-10-10', 'Returned'),
(2, 1, '2024-10-20', '2024-11-20', NULL, 'Checked Out'),
(3, 1, '2024-11-01', '2024-12-01', '2024-11-28', 'Returned'),
(4, 2, '2024-09-20', '2024-10-20', '2024-10-18', 'Returned'),
(5, 2, '2024-10-25', '2024-11-25', NULL, 'Checked Out'),
(6, 3, '2024-09-10', '2024-10-10', '2024-10-08', 'Returned');

-- Attendance
INSERT INTO Attendance (StudentID, ClassID, AttendanceDate, Status, Notes) VALUES
(1, 1, '2024-09-02', 'Present', NULL),
(1, 1, '2024-09-03', 'Present', NULL),
(1, 1, '2024-09-04', 'Absent', 'Sick'),
(1, 1, '2024-09-05', 'Present', NULL),
(1, 1, '2024-09-06', 'Present', NULL),
(2, 2, '2024-09-02', 'Present', NULL),
(2, 2, '2024-09-03', 'Tardy', 'Late 10 minutes'),
(2, 2, '2024-09-04', 'Present', NULL),
(3, 1, '2024-09-02', 'Present', NULL),
(3, 1, '2024-09-03', 'Present', NULL);

PRINT 'Database created successfully with sample data!';
GO
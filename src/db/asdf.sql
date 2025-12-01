/*
Patent Management System Database Schema
PostgreSQL 12+
Updated: 2025-12-01
Includes User authentication with JWT tokens, Author-based applications
*/

-- Table User (Authentication)
CREATE TABLE "User"
(
  "id" Serial NOT NULL,
  "email" Character varying NOT NULL UNIQUE,
  "username" Character varying NOT NULL UNIQUE,
  "hashed_password" Character varying NOT NULL,
  "is_active" Boolean DEFAULT true,
  "created_at" Timestamp DEFAULT CURRENT_TIMESTAMP,
  "user_type" Character varying NOT NULL,  -- 'employee' or 'author'
  "employee_id" Integer,
  "author_id" Integer
)
WITH (autovacuum_enabled=true);

ALTER TABLE "User" ADD CONSTRAINT "PK_User" PRIMARY KEY ("id");
CREATE INDEX "IX_User_email" ON "User" ("email");
CREATE INDEX "IX_User_username" ON "User" ("username");

-- Table Position
CREATE TABLE "Position"
(
  "id" Serial NOT NULL,
  "name" Character varying NOT NULL UNIQUE
)
WITH (autovacuum_enabled=true);

ALTER TABLE "Position" ADD CONSTRAINT "PK_Position" PRIMARY KEY ("id");

-- Table Passport
CREATE TABLE "Passport"
(
  "id" Serial NOT NULL,
  "series" Integer,
  "number" Integer,
  "birth_date" Date,
  "birth_place" Character varying,
  "department_code" Integer,
  "issued_by" Character varying
)
WITH (autovacuum_enabled=true);

ALTER TABLE "Passport" ADD CONSTRAINT "PK_Passport" PRIMARY KEY ("id");

-- Table Author
CREATE TABLE "Author"
(
  "id" Serial NOT NULL,
  "full_name" Character varying NOT NULL,
  "passport_id" Integer
)
WITH (autovacuum_enabled=true);

ALTER TABLE "Author" ADD CONSTRAINT "PK_Author" PRIMARY KEY ("id");
ALTER TABLE "Author" ADD CONSTRAINT "FK_Author_Passport" FOREIGN KEY ("passport_id") REFERENCES "Passport" ("id") ON DELETE CASCADE ON UPDATE RESTRICT;
CREATE INDEX "IX_Author_passport_id" ON "Author" ("passport_id");

-- Table Status
CREATE TABLE "Status"
(
  "id" Serial NOT NULL,
  "name" Character varying NOT NULL
)
WITH (autovacuum_enabled=true);

ALTER TABLE "Status" ADD CONSTRAINT "PK_Status" PRIMARY KEY ("id");

-- Table Employee
CREATE TABLE "Employee"
(
  "id" Serial NOT NULL,
  "full_name" Character varying NOT NULL,
  "employment_date" Date,
  "termination_date" Date,
  "phone_number" Character varying,
  "position_id" Integer,
  "passport_id" Integer
)
WITH (autovacuum_enabled=true);

ALTER TABLE "Employee" ADD CONSTRAINT "PK_Employee" PRIMARY KEY ("id");
ALTER TABLE "Employee" ADD CONSTRAINT "FK_Employee_Position" FOREIGN KEY ("position_id") REFERENCES "Position" ("id") ON DELETE RESTRICT ON UPDATE RESTRICT;
ALTER TABLE "Employee" ADD CONSTRAINT "FK_Employee_Passport" FOREIGN KEY ("passport_id") REFERENCES "Passport" ("id") ON DELETE CASCADE ON UPDATE RESTRICT;
CREATE INDEX "IX_Employee_position_id" ON "Employee" ("position_id");
CREATE INDEX "IX_Employee_passport_id" ON "Employee" ("passport_id");

-- Add foreign key for User.employee_id and User.author_id after tables created
ALTER TABLE "User" ADD CONSTRAINT "FK_User_Employee" FOREIGN KEY ("employee_id") REFERENCES "Employee" ("id") ON DELETE CASCADE ON UPDATE RESTRICT;
ALTER TABLE "User" ADD CONSTRAINT "FK_User_Author" FOREIGN KEY ("author_id") REFERENCES "Author" ("id") ON DELETE CASCADE ON UPDATE RESTRICT;
CREATE INDEX "IX_User_employee_id" ON "User" ("employee_id");
CREATE INDEX "IX_User_author_id" ON "User" ("author_id");

-- Table Application (can be created by authors or employees, managed by employees)
CREATE TABLE "Application"
(
  "id" Serial NOT NULL,
  "submission_date" Timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
  "documents" Text,
  "modification_date" Timestamp DEFAULT CURRENT_TIMESTAMP,
  "expert_conclusion" Text,
  "status_id" Integer,
  "employee_id" Integer,
  "author_id" Integer
)
WITH (autovacuum_enabled=true);

ALTER TABLE "Application" ADD CONSTRAINT "PK_Application" PRIMARY KEY ("id");
ALTER TABLE "Application" ADD CONSTRAINT "FK_Application_Status" FOREIGN KEY ("status_id") REFERENCES "Status" ("id") ON DELETE RESTRICT ON UPDATE RESTRICT;
ALTER TABLE "Application" ADD CONSTRAINT "FK_Application_Employee" FOREIGN KEY ("employee_id") REFERENCES "Employee" ("id") ON DELETE RESTRICT ON UPDATE RESTRICT;
ALTER TABLE "Application" ADD CONSTRAINT "FK_Application_Author" FOREIGN KEY ("author_id") REFERENCES "Author" ("id") ON DELETE RESTRICT ON UPDATE RESTRICT;
CREATE INDEX "IX_Application_status_id" ON "Application" ("status_id");
CREATE INDEX "IX_Application_employee_id" ON "Application" ("employee_id");
CREATE INDEX "IX_Application_author_id" ON "Application" ("author_id");

-- Table RightsHolder
CREATE TABLE "RightsHolder"
(
  "id" Serial NOT NULL,
  "name" Character varying NOT NULL
)
WITH (autovacuum_enabled=true);

ALTER TABLE "RightsHolder" ADD CONSTRAINT "PK_RightsHolder" PRIMARY KEY ("id");

-- Table PatentType
CREATE TABLE "PatentType"
(
  "id" Serial NOT NULL,
  "name" Character varying
)
WITH (autovacuum_enabled=true);

ALTER TABLE "PatentType" ADD CONSTRAINT "PK_PatentType" PRIMARY KEY ("id");

-- Table Patent
CREATE TABLE "Patent"
(
  "id" Serial NOT NULL,
  "title" Character varying,
  "issue_date" Date,
  "expiration_date" Date,
  "description" Character varying,
  "rights_holder_id" Integer,
  "patent_type_id" Integer,
  "status_id" Integer,
  "application_id" Integer NOT NULL
)
WITH (autovacuum_enabled=true);

ALTER TABLE "Patent" ADD CONSTRAINT "PK_Patent" PRIMARY KEY ("id");
ALTER TABLE "Patent" ADD CONSTRAINT "FK_Patent_RightsHolder" FOREIGN KEY ("rights_holder_id") REFERENCES "RightsHolder" ("id") ON DELETE RESTRICT ON UPDATE RESTRICT;
ALTER TABLE "Patent" ADD CONSTRAINT "FK_Patent_PatentType" FOREIGN KEY ("patent_type_id") REFERENCES "PatentType" ("id") ON DELETE RESTRICT ON UPDATE RESTRICT;
ALTER TABLE "Patent" ADD CONSTRAINT "FK_Patent_Status" FOREIGN KEY ("status_id") REFERENCES "Status" ("id") ON DELETE RESTRICT ON UPDATE RESTRICT;
ALTER TABLE "Patent" ADD CONSTRAINT "FK_Patent_Application" FOREIGN KEY ("application_id") REFERENCES "Application" ("id") ON DELETE CASCADE ON UPDATE RESTRICT;
CREATE INDEX "IX_Patent_rights_holder_id" ON "Patent" ("rights_holder_id");
CREATE INDEX "IX_Patent_patent_type_id" ON "Patent" ("patent_type_id");
CREATE INDEX "IX_Patent_status_id" ON "Patent" ("status_id");
CREATE INDEX "IX_Patent_application_id" ON "Patent" ("application_id");

-- Table PatentAuthor (Link table: Authors of each Patent)
CREATE TABLE "PatentAuthor"
(
  "author_id" Integer NOT NULL,
  "patent_id" Integer NOT NULL,
  "is_rights_holder" Boolean DEFAULT false,
  "participation_percentage" Numeric(5, 2)
)
WITH (autovacuum_enabled=true);

ALTER TABLE "PatentAuthor" ADD CONSTRAINT "PK_PatentAuthor" PRIMARY KEY ("author_id", "patent_id");
ALTER TABLE "PatentAuthor" ADD CONSTRAINT "FK_PatentAuthor_Author" FOREIGN KEY ("author_id") REFERENCES "Author" ("id") ON DELETE CASCADE ON UPDATE RESTRICT;
ALTER TABLE "PatentAuthor" ADD CONSTRAINT "FK_PatentAuthor_Patent" FOREIGN KEY ("patent_id") REFERENCES "Patent" ("id") ON DELETE RESTRICT ON UPDATE RESTRICT;
CREATE INDEX "IX_PatentAuthor_author_id" ON "PatentAuthor" ("author_id");
CREATE INDEX "IX_PatentAuthor_patent_id" ON "PatentAuthor" ("patent_id");

INSERT INTO "Status" ("name") VALUES 
  ('Создан'),
  ('Черновик'),
  ('Отправлен'),
  ('На рассмотрении'),
  ('Одобрен'),
  ('Отклонён'),
  ('Активен'),
  ('Истёкший'),
  ('На исправлении'),
  ('Отозван');

INSERT INTO "Position" ("name") VALUES 
  ('Патентный эксперт'),
  ('Начальник отдела'),
  ('папочка');

INSERT INTO "PatentType" ("name") VALUES 
  ('Изобретение'),
  ('Полезная модель'),
  ('Промышленный образец');

INSERT INTO "RightsHolder" ("id", "name") VALUES 
  (0, 'Правообладатель отсутствует');


PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS Citizen (
    Resident_ID TEXT PRIMARY KEY,
    Full_Name TEXT NOT NULL,
    Mobile_Number TEXT NOT NULL,
    Address TEXT NOT NULL,
    Is_Fictional INTEGER NOT NULL DEFAULT 1 CHECK (Is_Fictional = 1)
);

CREATE TABLE IF NOT EXISTS AuthorizedDealer (
    Dealer_ID TEXT PRIMARY KEY,
    Trade_Certificate_No TEXT NOT NULL UNIQUE,
    GSTIN TEXT NOT NULL UNIQUE,
    Business_Name TEXT NOT NULL,
    RTO_Jurisdiction_Code TEXT NOT NULL,
    Business_Address TEXT NOT NULL,
    Authorisation_Certificate_No TEXT NOT NULL UNIQUE,
    Authorisation_Issued_By TEXT NOT NULL,
    Authorisation_Valid_Until TEXT NOT NULL,
    Status TEXT NOT NULL DEFAULT 'ACTIVE'
        CHECK (Status IN ('ACTIVE', 'EXPIRED', 'SUSPENDED')),
    Is_Fictional INTEGER NOT NULL DEFAULT 1 CHECK (Is_Fictional = 1)
);

CREATE TABLE IF NOT EXISTS VehicleFixture (
    Vehicle_ID TEXT PRIMARY KEY,
    Vehicle_No TEXT NOT NULL UNIQUE,
    Chassis_Suffix TEXT NOT NULL,
    Chassis_No TEXT NOT NULL,
    Engine_Or_Motor_No TEXT NOT NULL,
    Seller_ID TEXT NOT NULL,
    Make_Model TEXT NOT NULL,
    RTO_Jurisdiction TEXT NOT NULL,
    Hypothecation_Active INTEGER NOT NULL DEFAULT 0
        CHECK (Hypothecation_Active IN (0, 1)),
    Is_Fictional INTEGER NOT NULL DEFAULT 1 CHECK (Is_Fictional = 1),
    FOREIGN KEY (Seller_ID) REFERENCES Citizen(Resident_ID)
);

CREATE TABLE IF NOT EXISTS HandoverCase (
    Case_ID TEXT PRIMARY KEY,
    Vehicle_No TEXT NOT NULL,
    Chassis_Suffix TEXT NOT NULL,
    Seller_ID TEXT NOT NULL,
    Dealer_ID TEXT,
    Current_State TEXT NOT NULL
        CHECK (Current_State IN ('DRAFT', 'INITIATED', 'DEALER_SELECTED', 'CUSTODY_TRANSFERRED')),
    Odometer_Reading INTEGER CHECK (Odometer_Reading IS NULL OR Odometer_Reading > 0),
    Delivery_Timestamp TEXT,
    Form_29C_Storage_URL TEXT,
    Created_At TEXT NOT NULL,
    Updated_At TEXT NOT NULL,
    FOREIGN KEY (Seller_ID) REFERENCES Citizen(Resident_ID),
    FOREIGN KEY (Dealer_ID) REFERENCES AuthorizedDealer(Dealer_ID)
);

CREATE TABLE IF NOT EXISTS StateTransitionLog (
    Transition_ID TEXT PRIMARY KEY,
    Case_ID TEXT NOT NULL,
    From_State TEXT NOT NULL,
    To_State TEXT NOT NULL,
    Transition_Timestamp TEXT NOT NULL,
    System_Integrity_Chaining_Hash TEXT NOT NULL,
    Previous_Transition_Hash TEXT,
    FOREIGN KEY (Case_ID) REFERENCES HandoverCase(Case_ID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Form29CDocument (
    Case_ID TEXT PRIMARY KEY,
    Pdf_Bytes BLOB NOT NULL,
    Sha256 TEXT NOT NULL,
    Generated_At TEXT NOT NULL,
    FOREIGN KEY (Case_ID) REFERENCES HandoverCase(Case_ID) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_handover_case_state ON HandoverCase(Current_State);
CREATE INDEX IF NOT EXISTS idx_transition_case_time
    ON StateTransitionLog(Case_ID, Transition_Timestamp);

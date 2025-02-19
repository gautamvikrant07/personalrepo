# Python script to recreate the database schema and data

import sqlite3


def create_db():
    conn = sqlite3.connect('../corep_large_exposure.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE ReportingEntity (
        entity_id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity_name TEXT NOT NULL,
        reporting_date DATE NOT NULL
    )''')
    cursor.execute('''CREATE TABLE Counterparty (
        counterparty_id INTEGER PRIMARY KEY AUTOINCREMENT,
        counterparty_name TEXT NOT NULL,
        counterparty_type TEXT NOT NULL, -- ENUM equivalent in SQLite
        country TEXT NOT NULL,
        sector TEXT NOT NULL
    , sector_id INTEGER, country_code INTEGER, lei INTEGER, type_of_counterparty varchar, group_of_connected_clients_id varchar, ultimate_parent_code varchar, accounting_portfolio varchar)''')
    cursor.execute('''CREATE TABLE ExposureType (
        exposure_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
        exposure_type_name TEXT NOT NULL
    )''')
    cursor.execute('''CREATE TABLE Metadata (
        table_name TEXT NOT NULL,
        column_name TEXT NOT NULL,
        description TEXT NOT NULL
    )''')
    cursor.execute('''CREATE TABLE Sector (
                sector_id INTEGER PRIMARY KEY,
                sector_name TEXT NOT NULL
            )''')
    cursor.execute('''CREATE TABLE Country (
                country_code TEXT PRIMARY KEY,
                country_name TEXT NOT NULL
            )''')
    cursor.execute('''CREATE TABLE Currency (
                currency_code TEXT PRIMARY KEY,
                currency_name TEXT NOT NULL
            )''')
    cursor.execute('''CREATE TABLE Risk_Weight (
                risk_weight_id INTEGER PRIMARY KEY,
                weight REAL NOT NULL
            )''')
    cursor.execute('''CREATE TABLE CRM_Technique (
                crm_id INTEGER PRIMARY KEY,
                crm_name TEXT NOT NULL,
                description TEXT
            )''')
    cursor.execute('''CREATE TABLE Exposure_Class (
                exposure_class_id INTEGER PRIMARY KEY,
                class_name TEXT NOT NULL
            )''')
    cursor.execute('''CREATE TABLE Instrument_Type (
                instrument_id INTEGER PRIMARY KEY,
                instrument_name TEXT NOT NULL
            )''')
    cursor.execute('''CREATE TABLE Connected_Client_Criteria (
                criteria_id INTEGER PRIMARY KEY,
                criteria_name TEXT NOT NULL
            )''')
    cursor.execute('''CREATE TABLE Exposure_Type (
                exposure_type_id INTEGER PRIMARY KEY,
                exposure_type TEXT NOT NULL
            )''')
    cursor.execute('''CREATE TABLE Large_Exposures (
                exposure_id INTEGER PRIMARY KEY,
                counterparty_id INTEGER,
                exposure_value REAL NOT NULL,
                crm_id INTEGER,
                net_exposure_after_crm REAL,
                risk_weight_id INTEGER,
                ead REAL,
                rwa REAL,
                exposure_class_id INTEGER,
                large_exposure_limit REAL,
                breaches BOOLEAN,
                instrument_id INTEGER,
                collateral_value REAL,
                currency_code TEXT,
                interest_rate REAL,
                maturity_date DATE,
                FOREIGN KEY (counterparty_id) REFERENCES Counterparty(counterparty_id),
                FOREIGN KEY (crm_id) REFERENCES CRM_Technique(crm_id),
                FOREIGN KEY (risk_weight_id) REFERENCES Risk_Weight(risk_weight_id),
                FOREIGN KEY (exposure_class_id) REFERENCES Exposure_Class(exposure_class_id),
                FOREIGN KEY (instrument_id) REFERENCES Instrument_Type(instrument_id),
                FOREIGN KEY (currency_code) REFERENCES Currency(currency_code)
            )''')
    cursor.execute('''CREATE TABLE Connected_Clients (
                client_id INTEGER PRIMARY KEY,
                group_id INTEGER,
                client_name TEXT NOT NULL,
                exposure_value REAL NOT NULL,
                crm_id INTEGER,
                net_exposure_value REAL,
                risk_weight_id INTEGER,
                rwa REAL,
                exposure_type_id INTEGER,
                criteria_id INTEGER,
                instrument_id INTEGER,
                currency_code TEXT,
                interest_rate REAL,
                maturity_date DATE,
                collateral_value REAL,
                crm_adjustments REAL,
                FOREIGN KEY (crm_id) REFERENCES CRM_Technique(crm_id),
                FOREIGN KEY (risk_weight_id) REFERENCES Risk_Weight(risk_weight_id),
                FOREIGN KEY (exposure_type_id) REFERENCES Exposure_Type(exposure_type_id),
                FOREIGN KEY (criteria_id) REFERENCES Connected_Client_Criteria(criteria_id),
                FOREIGN KEY (instrument_id) REFERENCES Instrument_Type(instrument_id),
                FOREIGN KEY (currency_code) REFERENCES Currency(currency_code)
            )''')
    cursor.execute('''CREATE TABLE XBRL_Corep_Le (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                xbrl_data TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )''')

    # Insert data
    cursor.execute(
        '''INSERT INTO ReportingEntity (entity_id, entity_name, reporting_date) VALUES (1, 'Bank A', '2024-08-01');''')
    cursor.execute(
        '''INSERT INTO ReportingEntity (entity_id, entity_name, reporting_date) VALUES (2, 'Bank B', '2024-08-01');''')
    cursor.execute('''INSERT INTO sqlite_sequence (name, seq) VALUES ('ReportingEntity', 2);''')
    cursor.execute('''INSERT INTO sqlite_sequence (name, seq) VALUES ('Counterparty', 2);''')
    cursor.execute('''INSERT INTO sqlite_sequence (name, seq) VALUES ('ExposureType', 3);''')
    cursor.execute('''INSERT INTO sqlite_sequence (name, seq) VALUES ('XBRL_Corep_Le', 1);''')
    cursor.execute(
        '''INSERT INTO Counterparty (counterparty_id, counterparty_name, counterparty_type, country, sector, sector_id, country_code, lei, type_of_counterparty, group_of_connected_clients_id, ultimate_parent_code, accounting_portfolio) VALUES (1, 'Counterparty X', 'Institution', 'UK', 'Finance', NULL, NULL, NULL, NULL, NULL, NULL, NULL);''')
    cursor.execute(
        '''INSERT INTO Counterparty (counterparty_id, counterparty_name, counterparty_type, country, sector, sector_id, country_code, lei, type_of_counterparty, group_of_connected_clients_id, ultimate_parent_code, accounting_portfolio) VALUES (2, 'Counterparty Y', 'Corporate', 'US', 'Technology', NULL, NULL, NULL, NULL, NULL, NULL, NULL);''')
    cursor.execute('''INSERT INTO ExposureType (exposure_type_id, exposure_type_name) VALUES (1, 'Trading Book');''')
    cursor.execute(
        '''INSERT INTO ExposureType (exposure_type_id, exposure_type_name) VALUES (2, 'Non-Trading Book');''')
    cursor.execute('''INSERT INTO ExposureType (exposure_type_id, exposure_type_name) VALUES (3, 'Securitization');''')
    cursor.execute(
        '''INSERT INTO Metadata (table_name, column_name, description) VALUES ('ReportingEntity', 'entity_id', 'Primary key, unique identifier for the reporting entity.');''')
    cursor.execute(
        '''INSERT INTO Metadata (table_name, column_name, description) VALUES ('ReportingEntity', 'entity_name', 'Name of the reporting entity.');''')
    cursor.execute(
        '''INSERT INTO Metadata (table_name, column_name, description) VALUES ('ReportingEntity', 'reporting_date', 'Date of the report.');''')
    cursor.execute(
        '''INSERT INTO Metadata (table_name, column_name, description) VALUES ('Counterparty', 'counterparty_id', 'Primary key, unique identifier for the counterparty.');''')
    cursor.execute(
        '''INSERT INTO Metadata (table_name, column_name, description) VALUES ('Counterparty', 'counterparty_name', 'Name of the counterparty.');''')
    cursor.execute(
        '''INSERT INTO Metadata (table_name, column_name, description) VALUES ('Counterparty', 'counterparty_type', 'Type of counterparty, e.g., Institution, Corporate.');''')
    cursor.execute(
        '''INSERT INTO Metadata (table_name, column_name, description) VALUES ('Counterparty', 'country', 'Country where the counterparty is located.');''')
    cursor.execute(
        '''INSERT INTO Metadata (table_name, column_name, description) VALUES ('Counterparty', 'sector', 'Sector to which the counterparty belongs.');''')
    cursor.execute(
        '''INSERT INTO Metadata (table_name, column_name, description) VALUES ('ExposureType', 'exposure_type_id', 'Primary key, unique identifier for the exposure type.');''')
    cursor.execute(
        '''INSERT INTO Metadata (table_name, column_name, description) VALUES ('ExposureType', 'exposure_type_name', 'Name of the exposure type, e.g., Trading Book, Non-Trading Book.');''')
    cursor.execute('''INSERT INTO Sector (sector_id, sector_name) VALUES (1, 'Non-financial corporations');''')
    cursor.execute('''INSERT INTO Sector (sector_id, sector_name) VALUES (2, 'Financial institutions');''')
    cursor.execute('''INSERT INTO Country (country_code, country_name) VALUES ('DEU', 'Germany');''')
    cursor.execute('''INSERT INTO Country (country_code, country_name) VALUES ('FRA', 'France');''')
    cursor.execute('''INSERT INTO Currency (currency_code, currency_name) VALUES ('EUR', 'Euro');''')
    cursor.execute('''INSERT INTO Currency (currency_code, currency_name) VALUES ('USD', 'US Dollar');''')
    cursor.execute('''INSERT INTO Risk_Weight (risk_weight_id, weight) VALUES (1, 100.0);''')
    cursor.execute('''INSERT INTO Risk_Weight (risk_weight_id, weight) VALUES (2, 75.0);''')
    cursor.execute(
        '''INSERT INTO CRM_Technique (crm_id, crm_name, description) VALUES (1, 'Collateral provided', 'Physical collateral or guarantees');''')
    cursor.execute(
        '''INSERT INTO CRM_Technique (crm_id, crm_name, description) VALUES (2, 'Guarantee', 'Third-party guarantee applied to exposure');''')
    cursor.execute('''INSERT INTO Exposure_Class (exposure_class_id, class_name) VALUES (1, 'Corporate');''')
    cursor.execute('''INSERT INTO Exposure_Class (exposure_class_id, class_name) VALUES (2, 'Institutional');''')
    cursor.execute('''INSERT INTO Instrument_Type (instrument_id, instrument_name) VALUES (1, 'Loan');''')
    cursor.execute('''INSERT INTO Instrument_Type (instrument_id, instrument_name) VALUES (2, 'Bond');''')
    cursor.execute('''INSERT INTO Connected_Client_Criteria (criteria_id, criteria_name) VALUES (1, 'Ownership');''')
    cursor.execute('''INSERT INTO Connected_Client_Criteria (criteria_id, criteria_name) VALUES (2, 'Control');''')
    cursor.execute('''INSERT INTO Exposure_Type (exposure_type_id, exposure_type) VALUES (1, 'Loan');''')
    cursor.execute('''INSERT INTO Exposure_Type (exposure_type_id, exposure_type) VALUES (2, 'Derivative');''')
    cursor.execute(
        '''INSERT INTO Large_Exposures (exposure_id, counterparty_id, exposure_value, crm_id, net_exposure_after_crm, risk_weight_id, ead, rwa, exposure_class_id, large_exposure_limit, breaches, instrument_id, collateral_value, currency_code, interest_rate, maturity_date) VALUES (1, 1, 200000000.0, 1, 150000000.0, 1, 150000000.0, 150000000.0, 1, 50000000.0, 0, 1, 50000000.0, 'EUR', 5.0, '2027-12-31');''')
    cursor.execute(
        '''INSERT INTO Large_Exposures (exposure_id, counterparty_id, exposure_value, crm_id, net_exposure_after_crm, risk_weight_id, ead, rwa, exposure_class_id, large_exposure_limit, breaches, instrument_id, collateral_value, currency_code, interest_rate, maturity_date) VALUES (2, 2, 300000000.0, 2, 280000000.0, 2, 210000000.0, 210000000.0, 2, 60000000.0, 0, 2, 100000000.0, 'USD', 3.5, '2028-06-30');''')
    cursor.execute(
        '''INSERT INTO Large_Exposures (exposure_id, counterparty_id, exposure_value, crm_id, net_exposure_after_crm, risk_weight_id, ead, rwa, exposure_class_id, large_exposure_limit, breaches, instrument_id, collateral_value, currency_code, interest_rate, maturity_date) VALUES (3, 3, 250000000.0, 1, 200000000.0, 1, 200000000.0, 200000000.0, 1, 55000000.0, 0, 1, 55000000.0, 'EUR', 4.75, '2027-11-30');''')
    cursor.execute(
        '''INSERT INTO Large_Exposures (exposure_id, counterparty_id, exposure_value, crm_id, net_exposure_after_crm, risk_weight_id, ead, rwa, exposure_class_id, large_exposure_limit, breaches, instrument_id, collateral_value, currency_code, interest_rate, maturity_date) VALUES (4, 4, 350000000.0, 2, 320000000.0, 2, 240000000.0, 240000000.0, 2, 70000000.0, 0, 2, 105000000.0, 'USD', 3.25, '2028-05-31');''')
    cursor.execute(
        '''INSERT INTO Large_Exposures (exposure_id, counterparty_id, exposure_value, crm_id, net_exposure_after_crm, risk_weight_id, ead, rwa, exposure_class_id, large_exposure_limit, breaches, instrument_id, collateral_value, currency_code, interest_rate, maturity_date) VALUES (5, 5, 180000000.0, 1, 140000000.0, 1, 140000000.0, 140000000.0, 1, 45000000.0, 0, 1, 45000000.0, 'EUR', 5.25, '2027-10-31');''')
    cursor.execute(
        '''INSERT INTO Large_Exposures (exposure_id, counterparty_id, exposure_value, crm_id, net_exposure_after_crm, risk_weight_id, ead, rwa, exposure_class_id, large_exposure_limit, breaches, instrument_id, collateral_value, currency_code, interest_rate, maturity_date) VALUES (6, 6, 220000000.0, 2, 210000000.0, 2, 157500000.0, 157500000.0, 2, 48000000.0, 0, 2, 90000000.0, 'USD', 3.75, '2028-07-31');''')
    cursor.execute(
        '''INSERT INTO Large_Exposures (exposure_id, counterparty_id, exposure_value, crm_id, net_exposure_after_crm, risk_weight_id, ead, rwa, exposure_class_id, large_exposure_limit, breaches, instrument_id, collateral_value, currency_code, interest_rate, maturity_date) VALUES (7, 7, 275000000.0, 1, 225000000.0, 1, 225000000.0, 225000000.0, 1, 65000000.0, 0, 1, 65000000.0, 'EUR', 4.85, '2027-09-30');''')
    cursor.execute(
        '''INSERT INTO Large_Exposures (exposure_id, counterparty_id, exposure_value, crm_id, net_exposure_after_crm, risk_weight_id, ead, rwa, exposure_class_id, large_exposure_limit, breaches, instrument_id, collateral_value, currency_code, interest_rate, maturity_date) VALUES (8, 8, 330000000.0, 2, 300000000.0, 2, 225000000.0, 225000000.0, 2, 69000000.0, 0, 2, 110000000.0, 'USD', 3.15, '2028-04-30');''')
    cursor.execute(
        '''INSERT INTO Large_Exposures (exposure_id, counterparty_id, exposure_value, crm_id, net_exposure_after_crm, risk_weight_id, ead, rwa, exposure_class_id, large_exposure_limit, breaches, instrument_id, collateral_value, currency_code, interest_rate, maturity_date) VALUES (9, 9, 190000000.0, 1, 145000000.0, 1, 145000000.0, 145000000.0, 1, 47000000.0, 0, 1, 47000000.0, 'EUR', 5.1, '2027-08-31');''')
    cursor.execute(
        '''INSERT INTO Large_Exposures (exposure_id, counterparty_id, exposure_value, crm_id, net_exposure_after_crm, risk_weight_id, ead, rwa, exposure_class_id, large_exposure_limit, breaches, instrument_id, collateral_value, currency_code, interest_rate, maturity_date) VALUES (10, 10, 310000000.0, 2, 285000000.0, 2, 213750000.0, 213750000.0, 2, 67000000.0, 0, 2, 102500000.0, 'USD', 3.65, '2028-03-31');''')
    cursor.execute(
        '''INSERT INTO Connected_Clients (client_id, group_id, client_name, exposure_value, crm_id, net_exposure_value, risk_weight_id, rwa, exposure_type_id, criteria_id, instrument_id, currency_code, interest_rate, maturity_date, collateral_value, crm_adjustments) VALUES (1, 1, 'John Doe', 50000000.0, 2, 45000000.0, 1, 45000000.0, 1, 1, 1, 'EUR', 5.0, '2027-12-31', 20000000.0, 5000000.0);''')
    cursor.execute(
        '''INSERT INTO Connected_Clients (client_id, group_id, client_name, exposure_value, crm_id, net_exposure_value, risk_weight_id, rwa, exposure_type_id, criteria_id, instrument_id, currency_code, interest_rate, maturity_date, collateral_value, crm_adjustments) VALUES (2, 2, 'Jane Smith', 75000000.0, 1, 70000000.0, 2, 56000000.0, 2, 2, 2, 'USD', 3.5, '2028-06-30', 30000000.0, 10000000.0);''')
    cursor.execute(
        '''INSERT INTO Connected_Clients (client_id, group_id, client_name, exposure_value, crm_id, net_exposure_value, risk_weight_id, rwa, exposure_type_id, criteria_id, instrument_id, currency_code, interest_rate, maturity_date, collateral_value, crm_adjustments) VALUES (3, 3, 'Alice Johnson', 60000000.0, 2, 55000000.0, 1, 55000000.0, 1, 1, 1, 'EUR', 4.75, '2027-11-30', 25000000.0, 7500000.0);''')
    cursor.execute(
        '''INSERT INTO Connected_Clients (client_id, group_id, client_name, exposure_value, crm_id, net_exposure_value, risk_weight_id, rwa, exposure_type_id, criteria_id, instrument_id, currency_code, interest_rate, maturity_date, collateral_value, crm_adjustments) VALUES (4, 4, 'Bob Brown', 85000000.0, 1, 80000000.0, 2, 64000000.0, 2, 2, 2, 'USD', 3.25, '2028-05-31', 35000000.0, 12500000.0);''')
    cursor.execute(
        '''INSERT INTO Connected_Clients (client_id, group_id, client_name, exposure_value, crm_id, net_exposure_value, risk_weight_id, rwa, exposure_type_id, criteria_id, instrument_id, currency_code, interest_rate, maturity_date, collateral_value, crm_adjustments) VALUES (5, 5, 'Charlie Green', 40000000.0, 2, 35000000.0, 1, 35000000.0, 1, 1, 1, 'EUR', 5.25, '2027-10-31', 15000000.0, 5000000.0);''')
    cursor.execute(
        '''INSERT INTO Connected_Clients (client_id, group_id, client_name, exposure_value, crm_id, net_exposure_value, risk_weight_id, rwa, exposure_type_id, criteria_id, instrument_id, currency_code, interest_rate, maturity_date, collateral_value, crm_adjustments) VALUES (6, 6, 'Diana White', 70000000.0, 1, 65000000.0, 2, 52000000.0, 2, 2, 2, 'USD', 3.75, '2028-07-31', 28000000.0, 9500000.0);''')
    cursor.execute(
        '''INSERT INTO Connected_Clients (client_id, group_id, client_name, exposure_value, crm_id, net_exposure_value, risk_weight_id, rwa, exposure_type_id, criteria_id, instrument_id, currency_code, interest_rate, maturity_date, collateral_value, crm_adjustments) VALUES (7, 7, 'Evan Black', 80000000.0, 2, 75000000.0, 1, 75000000.0, 1, 1, 1, 'EUR', 4.85, '2027-09-30', 30000000.0, 10000000.0);''')
    cursor.execute(
        '''INSERT INTO Connected_Clients (client_id, group_id, client_name, exposure_value, crm_id, net_exposure_value, risk_weight_id, rwa, exposure_type_id, criteria_id, instrument_id, currency_code, interest_rate, maturity_date, collateral_value, crm_adjustments) VALUES (8, 8, 'Fiona Grey', 90000000.0, 1, 85000000.0, 2, 68000000.0, 2, 2, 2, 'USD', 3.15, '2028-04-30', 35000000.0, 11500000.0);''')
    cursor.execute(
        '''INSERT INTO Connected_Clients (client_id, group_id, client_name, exposure_value, crm_id, net_exposure_value, risk_weight_id, rwa, exposure_type_id, criteria_id, instrument_id, currency_code, interest_rate, maturity_date, collateral_value, crm_adjustments) VALUES (9, 9, 'George Silver', 55000000.0, 2, 50000000.0, 1, 50000000.0, 1, 1, 1, 'EUR', 5.1, '2027-08-31', 25000000.0, 7500000.0);''')
    cursor.execute(
        '''INSERT INTO Connected_Clients (client_id, group_id, client_name, exposure_value, crm_id, net_exposure_value, risk_weight_id, rwa, exposure_type_id, criteria_id, instrument_id, currency_code, interest_rate, maturity_date, collateral_value, crm_adjustments) VALUES (10, 10, 'Helen Gold', 77000000.0, 1, 72000000.0, 2, 57600000.0, 2, 2, 2, 'USD', 3.65, '2028-03-31', 29000000.0, 9000000.0);''')
    cursor.execute('''INSERT INTO XBRL_Corep_Le (id, xbrl_data, created_at) VALUES (1, '<xbrl xmlns="http://www.xbrl.org/2003/instance"
      xmlns:link="http://www.xbrl.org/2003/linkbase"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xmlns:c27="http://www.eba.europa.eu/xbrl/c27"
      xmlns:c28="http://www.eba.europa.eu/xbrl/c28"
      xmlns:c29="http://www.eba.europa.eu/xbrl/c29">

    <!-- Context Definitions -->
    <context id="Context_Entity_001_2023">
        <entity>
            <identifier scheme="http://www.example.com/entity">ENTITY_001</identifier>
        </entity>
        <period>
            <startDate>2023-01-01</startDate>
            <endDate>2023-12-31</endDate>
        </period>
        <scenario>
            <c27:ScenarioType>Baseline</c27:ScenarioType>
        </scenario>
    </context>

    <context id="Context_Entity_002_2023">
        <entity>
            <identifier scheme="http://www.example.com/entity">ENTITY_002</identifier>
        </entity>
        <period>
            <startDate>2023-01-01</startDate>
            <endDate>2023-12-31</endDate>
        </period>
        <scenario>
            <c27:ScenarioType>Adverse</c27:ScenarioType>
        </scenario>
    </context>

    <!-- Units Declaration -->
    <unit id="EUR">
        <measure>iso4217:EUR</measure>
    </unit>
    <unit id="USD">
        <measure>iso4217:USD</measure>
    </unit>

    <!-- C27: Counterparty Data -->
    <c27:Counterparty contextRef="Context_Entity_001_2023">
        <c27:CounterpartyID>1</c27:CounterpartyID>
        <c27:CounterpartyName>XYZ Corporation</c27:CounterpartyName>
        <c27:Sector>Non-financial corporations</c27:Sector>
        <c27:CountryCode>DEU</c27:CountryCode>
        <c27:LEI>1234567890ABCDEF</c27:LEI>
        <c27:TypeOfCounterparty>Corporate</c27:TypeOfCounterparty>
        <c27:GroupOfConnectedClientsID>GCC001</c27:GroupOfConnectedClientsID>
        <c27:UltimateParentCode>PARENT001</c27:UltimateParentCode>
        <c27:AccountingPortfolio>Non-Trading</c27:AccountingPortfolio>
        <c27:CRM>
            <c27:CRMType>Collateral</c27:CRMType>
            <c27:CRMValue unitRef="EUR">50000000</c27:CRMValue>
            <c27:CollateralType>Real Estate</c27:CollateralType>
        </c27:CRM>
    </c27:Counterparty>

    <c27:Counterparty contextRef="Context_Entity_002_2023">
        <c27:CounterpartyID>2</c27:CounterpartyID>
        <c27:CounterpartyName>ABC Bank</c27:CounterpartyName>
        <c27:Sector>Financial institutions</c27:Sector>
        <c27:CountryCode>FRA</c27:CountryCode>
        <c27:LEI>9876543210ZYXWVU</c27:LEI>
        <c27:TypeOfCounterparty>Institutional</c27:TypeOfCounterparty>
        <c27:GroupOfConnectedClientsID>GCC002</c27:GroupOfConnectedClientsID>
        <c27:UltimateParentCode>PARENT002</c27:UltimateParentCode>
        <c27:AccountingPortfolio>Trading</c27:AccountingPortfolio>
        <c27:CRM>
            <c27:CRMType>Guarantee</c27:CRMType>
            <c27:CRMValue unitRef="USD">100000000</c27:CRMValue>
            <c27:CollateralType>Bank Guarantee</c27:CollateralType>
        </c27:CRM>
    </c27:Counterparty>

    <!-- C28: Large Exposures Data -->
    <c28:LargeExposure contextRef="Context_Entity_001_2023" unitRef="EUR">
        <c28:ExposureID>LE001</c28:ExposureID>
        <c28:CounterpartyID>1</c28:CounterpartyID>
        <c28:ExposureValue>200000000</c28:ExposureValue>
        <c28:CRMType>Collateral provided</c28:CRMType>
        <c28:NetExposureAfterCRM>150000000</c28:NetExposureAfterCRM>
        <c28:RiskWeight>100.00</c28:RiskWeight>
        <c28:EAD>150000000</c28:EAD>
        <c28:RWA>150000000</c28:RWA>
        <c28:ExposureClass>Corporate</c28:ExposureClass>
        <c28:LargeExposureLimit>50000000</c28:LargeExposureLimit>
        <c28:Breaches>false</c28:Breaches>
        <c28:InstrumentType>Loan</c28:InstrumentType>
        <c28:CollateralValue>50000000</c28:CollateralValue>
        <c28:Currency>EUR</c28:Currency>
        <c28:InterestRate>5.00</c28:InterestRate>
        <c28:MaturityDate>2027-12-31</c28:MaturityDate>
        <c28:ResidualMaturity>4 years</c28:ResidualMaturity>
        <c28:CapitalRequirementCalculationMethod>Standardized Approach</c28:CapitalRequirementCalculationMethod>
        <c28:CreditRiskMitigationMethod>Financial Collateral Simple Method</c28:CreditRiskMitigationMethod>
    </c28:LargeExposure>

    <c28:LargeExposure contextRef="Context_Entity_002_2023" unitRef="USD">
        <c28:ExposureID>LE002</c28:ExposureID>
        <c28:CounterpartyID>2</c28:CounterpartyID>
        <c28:ExposureValue>300000000</c28:ExposureValue>
        <c28:CRMType>Guarantee</c28:CRMType>
        <c28:NetExposureAfterCRM>280000000</c28:NetExposureAfterCRM>
        <c28:RiskWeight>75.00</c28:RiskWeight>
        <c28:EAD>210000000</c28:EAD>
        <c28:RWA>210000000</c28:RWA>
        <c28:ExposureClass>Institutional</c28:ExposureClass>
        <c28:LargeExposureLimit>60000000</c28:LargeExposureLimit>
        <c28:Breaches>false</c28:Breaches>
        <c28:InstrumentType>Bond</c28:InstrumentType>
        <c28:CollateralValue>100000000</c28:CollateralValue>
        <c28:Currency>USD</c28:Currency>
        <c28:InterestRate>3.50</c28:InterestRate>
        <c28:MaturityDate>2028-06-30</c28:MaturityDate>
        <c28:ResidualMaturity>5 years</c28:ResidualMaturity>
        <c28:CapitalRequirementCalculationMethod>Internal Ratings-Based Approach</c28:CapitalRequirementCalculationMethod>
        <c28:CreditRiskMitigationMethod>Guarantees and Credit Derivatives</c28:CreditRiskMitigationMethod>
    </c28:LargeExposure>


    <!-- C29: Connected Clients Data -->
    <c29:ConnectedClient contextRef="Context_Entity_001_2023" unitRef="EUR">
        <c29:ClientID>CC001</c29:ClientID>
        <c29:GroupID>GCC001</c29:GroupID>
        <c29:ClientName>John Doe</c29:ClientName>
        <c29:ExposureValue>50000000</c29:ExposureValue>
        <c29:CRMType>Guarantee</c29:CRMType>
        <c29:NetExposureValue>45000000</c29:NetExposureValue>
        <c29:RiskWeight>100.00</c29:RiskWeight>
        <c29:RWA>45000000</c29:RWA>
        <c29:ExposureType>Loan</c29:ExposureType>
        <c29:Criteria>Ownership</c29:Criteria>
        <c29:InstrumentType>Loan</c29:InstrumentType>
        <c29:Currency>EUR</c29:Currency>
        <c29:InterestRate>5.00</c29:InterestRate>
        <c29:MaturityDate>2027-12-31</c29:MaturityDate>
        <c29:CollateralValue>20000000</c29:CollateralValue>
        <c29:CRMAdjustments>5000000</c29:CRMAdjustments>
        <c29:ExposureMitigationStrategy>Credit Default Swap</c29:ExposureMitigationStrategy>
        <c29:CapitalRequirementContribution>20%</c29:CapitalRequirementContribution>
    </c29:ConnectedClient>

    <c29:ConnectedClient contextRef="Context_Entity_002_2023" unitRef="USD">
        <c29:ClientID>CC002</c29:ClientID>
        <c29:GroupID>GCC002</c29:GroupID>
        <c29:ClientName>Jane Smith</c29:ClientName>
        <c29:ExposureValue>75000000</c29:ExposureValue>
        <c29:CRMType>Collateral</c29:CRMType>
        <c29:NetExposureValue>70000000</c29:NetExposureValue>
        <c29:RiskWeight>75.00</c29:RiskWeight>
        <c29:RWA>52500000</c29:RWA>
        <c29:ExposureType>Bond</c29:ExposureType>
        <c29:Criteria>Control</c29:Criteria>
        <c29:InstrumentType>Bond</c29:InstrumentType>
        <c29:Currency>USD</c29:Currency>
        <c29:InterestRate>3.75</c29:InterestRate>
        <c29:MaturityDate>2028-06-30</c29:MaturityDate>
        <c29:CollateralValue>30000000</c29:CollateralValue>
        <c29:CRMAdjustments>7500000</c29:CRMAdjustments>
        <c29:ExposureMitigationStrategy>Guarantees</c29:ExposureMitigationStrategy>
        <c29:CapitalRequirementContribution>18%</c29:CapitalRequirementContribution>
    </c29:ConnectedClient>

</xbrl>
', '2024-08-25 18:23:30');''')

    conn.commit()
    conn.close()


if __name__ == '__main__':
    create_db()

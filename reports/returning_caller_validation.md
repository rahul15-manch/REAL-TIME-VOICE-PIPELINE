# Returning Caller Persistence Validation

## 1. Test Objective
The objective of this test is to validate that a returning caller is correctly identified using their stored phone number, and that their existing client record is reused instead of creating a duplicate row in the Neon PostgreSQL database.

## 2. Execution Steps
1. Connected to the configured Neon PostgreSQL database using `DATABASE_URL`.
2. Chosen a test phone number: `+919999999999`.
3. Purged any existing test data for `+919999999999` to ensure a clean state.
4. Simulated a first incoming call using `ClientRepository.get_or_create_client`.
5. Simulated a second incoming call using the exact same phone number via the same repository method.
6. Queried the database to confirm only one client record exists.

## 3. SQL Validation
Query executed:
```sql
SELECT COUNT(*) FROM clients WHERE phone_number = '+919999999999';
```
Result: `1`

## 4. Repository Validation
- Repository Pattern was preserved; all database interactions occurred through `ClientRepository`.
- Asynchronous execution was used via SQLAlchemy 2.0 AsyncSessions.
- No raw SQL outside the repository layer was used for standard operations (only for validation assertions).

## 5. Assertions
- ✅ First call creates one client
- ✅ Second call returns the same client
- ✅ UUID remains identical
- ✅ Phone number remains identical
- ✅ No duplicate client rows exist
- ✅ UNIQUE constraint is respected
- ✅ Repository returns existing object
- ✅ No raw SQL outside repository layer

## 6. Logs
```
FIRST CALL:
UUID: f73a81b0-7c2f-4191-a652-5a5f69fc4087
Phone Number: +919999999999
Created Timestamp: 2026-07-12 06:03:04.940775

SECOND CALL:
UUID: f73a81b0-7c2f-4191-a652-5a5f69fc4087
Phone Number: +919999999999
Updated Timestamp: 2026-07-12 06:03:04.940780

DATABASE VALIDATION:
Count: 1
```

## 7. Result
The returning caller reused the existing client record. The repository returned the previously created UUID and no additional `INSERT` occurred, thereby preventing duplicate client profiles.

## 8. Pass/Fail
**PASS**

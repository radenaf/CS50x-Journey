-- Keep a log of any SQL queries you execute as you solve the mystery.

SELECT * FROM crime_scene_reports
WHERE street = 'Humphrey Street';
--Bakery Witness--
SELECT * FROM interviews
WHERE transcript LIKE '%bakery%';
--Theft at 10:15--
--Witness 1 ruth--
SELECT * FROM bakery_security_logs
WHERE year = 2025 AND month = 7 AND day = 28 AND hour = 10 AND minute BETWEEN 15 AND 30;
--check license plate--
SELECT p.name, bsl.activity, bsl.license_plate, bsl.year, bsl.month, bsl.day, bsl.hour, bsl.minute
FROM bakery_security_logs bsl
JOIN people p ON bsl.license_plate = p.license_plate
WHERE bsl.year = 2025 AND bsl.month = 7 AND bsl.day = 28 AND bsl.hour = 10 AND bsl.minute BETWEEN 15 AND 30;
--Witness 2 Eugene--
SELECT * FROM atm_transactions
WHERE atm_location = 'Leggett Street'
AND year = 2025 AND month = 7 AND day = 28;
--add name of withdraws from atm--
SELECT a.*, p.name
FROM atm_transactions a
JOIN bank_accounts b ON a.account_number = b.account_number
JOIN people p ON b.person_id = p.id
WHERE a.atm_location = 'Leggett Street'
AND a.year = 2025 AND a.month = 7 AND a.day = 28;
--WITNESS 3:call--
SELECT * FROM phone_calls
WHERE year = 2025 AND month = 7 AND day = 28 AND duration < 60;
--GET NAME OF CALLER--
SELECT p.name, pc.caller, pc.receiver, pc.year, pc.month, pc.day, pc.duration
FROM phone_calls pc
JOIN people p ON pc.caller = p.phone_number
WHERE pc.year = 2025 AND pc.month = 7 AND pc.day = 28 AND pc.duration < 60;
--find fiftyville airport 8--
SELECT * FROM airports
--Found the airport explore out--
SELECT f.*, origin.full_name AS origin_airport, destination.full_name AS destination_airport
FROM flights f
JOIN airports origin ON f.origin_airport_id = origin.id
JOIN airports destination ON f.destination_airport_id = destination.id
WHERE origin.id = 8 AND f.year = 2025 AND f.month = 7 AND f.day = 29
ORDER BY f.hour, f.minute;
--combine info from all three testimonies to find the suspect--
SELECT p.name
FROM bakery_security_logs bsl
JOIN people p ON bsl.license_plate = p.license_plate
Join bank_accounts ba ON p.id = ba.person_id
JOIN atm_transactions at ON ba.account_number = at.account_number
JOIN phone_calls pc ON p.phone_number = pc.caller
WHERE bsl.year = 2025 AND bsl.month = 7 AND bsl.day = 28 AND bsl.hour = 10 AND bsl.minute BETWEEN 15 AND 30
AND at.atm_location = 'Leggett Street' AND at.year = 2025 AND at.month = 7 AND at.day = 28
AND pc.year = 2025 AND pc.month = 7 AND pc.day = 28 AND pc.duration < 60;

--Check flights for the suspect FLIGHT 36--
SELECT p.name
FROM people p
JOIN passengers ps ON p.passport_number = ps.passport_number
WHERE ps.flight_id = 36
AND p.name IN ('Bruce', 'Diana');

--Who Bruce Called--
SELECT p2.name AS receiver
FROM phone_calls pc
JOIN people p1 ON pc.caller = p1.phone_number
JOIN people p2 ON pc.receiver = p2.phone_number
WHERE p1.name = 'Bruce'
AND pc.year = 2025 AND pc.month = 7 AND pc.day = 28
AND pc.duration < 60;


--Заходим в postgres как пользователь postgres, создаём базу данных и две роли, даем права этим ролям
CREATE DATABASE russwimming_db;

CREATE ROLE administrator WITH LOGIN PASSWORD 'di_ego';
CREATE ROLE avg_user WITH LOGIN PASSWORD 'userxfa';

GRANT ALL PRIVILEGES ON DATABASE russwimming_db TO administrator;
ALTER DATABASE russwimming_db OWNER TO administrator;
GRANT CONNECT ON DATABASE russwimming_db TO avg_user;

--Переподключаемся уже к созданной БД как пользователь administrator и создаём следующие функции (и индекс)
CREATE OR REPLACE FUNCTION create_tables()
RETURNS VOID AS $$
BEGIN
    CREATE TABLE Region (
        region_code CHAR(3) PRIMARY KEY,
        region_name VARCHAR(100),
        federal_district VARCHAR(100),
        team_leader VARCHAR(100),
        athlete_count INT
    );

    CREATE TABLE Athlete (
        id_athlete SERIAL PRIMARY KEY,
        surname VARCHAR(50),
        athlete_name VARCHAR(50),
        birth_year INT CHECK (birth_year >= 1908 AND birth_year <= EXTRACT(YEAR FROM CURRENT_DATE)),
        rank VARCHAR(4),
        gender CHAR(1),
        code_region CHAR(3) REFERENCES Region(region_code)
    );

    CREATE TABLE Competition (
        id_competition SERIAL PRIMARY KEY,
        title VARCHAR(100),
        city VARCHAR(50),
        competition_level VARCHAR(50),
        begin_date DATE,
        end_date DATE,
        age_group VARCHAR(50),
        pool_length INT
    );

    CREATE TABLE Result (
        id_result SERIAL PRIMARY KEY,
        discipline_length INT,
        discipline_style VARCHAR(50),
        time_result VARCHAR(8),
        points INT,
        result_date DATE,
        place INT,
        competition_id INT REFERENCES Competition(id_competition),
        athlete_id INT REFERENCES Athlete(id_athlete)
    );

    GRANT SELECT ON TABLE Region TO avg_user;
    GRANT SELECT ON TABLE Athlete TO avg_user;
    GRANT SELECT ON TABLE Competition TO avg_user;
    GRANT SELECT ON TABLE Result TO avg_user;

    GRANT USAGE, SELECT ON SEQUENCE athlete_id_athlete_seq TO avg_user;
    GRANT USAGE, SELECT ON SEQUENCE competition_id_competition_seq TO avg_user;
    GRANT USAGE, SELECT ON SEQUENCE result_id_result_seq TO avg_user;

    CREATE TRIGGER increment_athlete_count_after_insert
    AFTER INSERT ON Athlete
    FOR EACH ROW
    EXECUTE FUNCTION update_athlete_count();

    CREATE TRIGGER decrement_athlete_count_after_delete
    AFTER DELETE ON Athlete
    FOR EACH ROW
    EXECUTE FUNCTION update_athlete_count();

    CREATE INDEX idx_athlete_search ON Athlete(surname, athlete_name, birth_year, rank, gender, code_region);
END;
$$
 LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION drop_tables()
RETURNS VOID AS $$
BEGIN
    DROP TABLE IF EXISTS Result CASCADE;
    DROP TABLE IF EXISTS Athlete CASCADE;
    DROP TABLE IF EXISTS Competition CASCADE;
    DROP TABLE IF EXISTS Region CASCADE;
END;
$$
 LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION add_athlete(surname VARCHAR, athlete_name VARCHAR, birth_year INT, rank VARCHAR, gender CHAR, code_region CHAR) RETURNS VOID AS $$
BEGIN
    INSERT INTO Athlete (surname, athlete_name, birth_year, rank, gender, code_region) VALUES (surname, athlete_name, birth_year, rank, gender, code_region);
END;
$$
 LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION add_competition(title VARCHAR, city VARCHAR, competition_level VARCHAR, begin_date DATE, end_date DATE, age_group VARCHAR, pool_length INT) RETURNS VOID AS $$
BEGIN
    INSERT INTO Competition (title, city, competition_level, begin_date, end_date, age_group, pool_length) VALUES (title, city, competition_level, begin_date, end_date, age_group, pool_length);
END;
$$
 LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION add_result(discipline_length INT, discipline_style VARCHAR, time_result VARCHAR, points INT, result_date DATE, place INT, competition_id INT, athlete_id INT) RETURNS VOID AS $$
BEGIN
    INSERT INTO Result (discipline_length, discipline_style, time_result, points, result_date, place, competition_id, athlete_id) VALUES (discipline_length, discipline_style, time_result, points, result_date, place, competition_id, athlete_id);
END;
$$
 LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION delete_athlete(s VARCHAR, a_n VARCHAR, b_y INT, r VARCHAR, g CHAR, c_r CHAR) RETURNS VOID AS $$
BEGIN
    DELETE FROM Athlete WHERE surname = s AND athlete_name = a_n AND birth_year = b_y AND rank = r AND gender = g AND code_region = c_r;
END;
$$
 LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION add_region(region_code CHAR, region_name VARCHAR, federal_district VARCHAR, team_leader VARCHAR) RETURNS VOID AS $$
BEGIN
    INSERT INTO Region (region_code, region_name, federal_district, team_leader, athlete_count) VALUES (region_code, region_name, federal_district, team_leader, 0);
END;
$$
 LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_athlete(
    p_id_athlete INT,
    p_surname VARCHAR,
    p_athlete_name VARCHAR,
    p_birth_year INT,
    p_rank VARCHAR,
    p_gender CHAR,
    p_code_region CHAR
) 
RETURNS VOID AS $$
BEGIN
    UPDATE Athlete
    SET 
        surname = p_surname,
        athlete_name = p_athlete_name,
        birth_year = p_birth_year,
        rank = p_rank,
        gender = p_gender,
        code_region = p_code_region
    WHERE id_athlete = p_id_athlete;
END;
$$
 LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_athlete_id(
    p_surname VARCHAR,
    p_athlete_name VARCHAR,
    p_birth_year INT,
    p_rank VARCHAR,
    p_gender CHAR,
    p_code_region CHAR
) 
RETURNS INT AS $$
DECLARE
    athlete_id INT;
BEGIN
    SELECT id_athlete INTO athlete_id
    FROM Athlete
    WHERE surname = p_surname 
      AND athlete_name = p_athlete_name 
      AND birth_year = p_birth_year 
      AND rank = p_rank 
      AND gender = p_gender 
      AND code_region = p_code_region;
    RETURN athlete_id;
END;
$$
 LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION clear_athlete_data()
RETURNS VOID AS $$
BEGIN
    DELETE FROM Athlete;
END;
$$
 LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION clear_all_data()
RETURNS VOID AS $$
BEGIN
    DELETE FROM Result;
    DELETE FROM Athlete;
    DELETE FROM Competition;
    DELETE FROM Region;
END;
$$
 LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_athletes()
RETURNS TABLE(id_athlete INT, surname VARCHAR, athlete_name VARCHAR, birth_year INT, rank VARCHAR, gender CHAR, code_region CHAR(3)) AS $$
BEGIN
    RETURN QUERY
    SELECT a.id_athlete, a.surname, a.athlete_name, a.birth_year, a.rank, a.gender, a.code_region
    FROM Athlete a;
END;
$$
 LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_competitions()
RETURNS TABLE(id_competition INT, title VARCHAR, city VARCHAR, begin_date DATE, end_date DATE, pool_length INT) AS $$
BEGIN
    RETURN QUERY
    SELECT c.id_competition, c.title, c.city, c.begin_date, c.end_date, c.pool_length
    FROM Competition c;
END;
$$
 LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_regions()
RETURNS TABLE (
    region_code CHAR(3),
    region_name VARCHAR(100),
    federal_district VARCHAR(100),
    team_leader VARCHAR(100),
    athlete_count INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT r.region_code, r.region_name, r.federal_district, r.team_leader, r.athlete_count
    FROM Region r;
END;
$$
 LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION delete_region(del_region_code CHAR(3))
RETURNS VOID AS $$
BEGIN
    DELETE FROM Athlete
    WHERE code_region = del_region_code;

    DELETE FROM Region
    WHERE region_code = del_region_code;
END;
$$
 LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_athlete_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE Region
        SET athlete_count = athlete_count + 1
        WHERE region_code = NEW.code_region;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE Region
        SET athlete_count = GREATEST(0, athlete_count - 1)
        WHERE region_code = OLD.code_region;
    END IF;

    RETURN NEW;
END;
$$
 LANGUAGE plpgsql;

--GRANT EXECUTE ON FUNCTION create_tables() TO administrator;
--GRANT EXECUTE ON FUNCTION drop_tables() TO administrator;
--GRANT EXECUTE ON FUNCTION add_athlete(VARCHAR, VARCHAR, INT, VARCHAR, CHAR, CHAR) TO administrator;
--GRANT EXECUTE ON FUNCTION add_competition(VARCHAR, VARCHAR, VARCHAR, DATE, DATE, VARCHAR, INT) TO administrator;
--GRANT EXECUTE ON FUNCTION add_result(INT, VARCHAR, VARCHAR, INT, DATE, INT, INT, INT) TO administrator;
--GRANT EXECUTE ON FUNCTION delete_athlete(VARCHAR, VARCHAR, INT, VARCHAR, CHAR, CHAR) TO administrator;
--GRANT EXECUTE ON FUNCTION add_region(CHAR, VARCHAR, VARCHAR, VARCHAR) TO administrator;
--GRANT EXECUTE ON FUNCTION update_athlete(INT, VARCHAR, VARCHAR, INT, VARCHAR, CHAR, CHAR) TO administrator;
--GRANT EXECUTE ON FUNCTION get_athlete_id(VARCHAR, VARCHAR, INT, VARCHAR, CHAR, CHAR) TO administrator;
--GRANT EXECUTE ON FUNCTION clear_athlete_data() TO administrator;
--GRANT EXECUTE ON FUNCTION clear_all_data() to administrator;

--GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE Region TO administrator;
--GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE Athlete TO administrator;
--GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE Competition TO administrator;
--GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE Result TO administrator;

--GRANT USAGE, SELECT, UPDATE ON SEQUENCE athlete_id_athlete_seq TO administrator;
--GRANT USAGE, SELECT, UPDATE ON SEQUENCE competition_id_competition_seq TO administrator;
--GRANT USAGE, SELECT, UPDATE ON SEQUENCE result_id_result_seq TO administrator;

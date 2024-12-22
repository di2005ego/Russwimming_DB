--Затем создаём две самые главные функции и даем права на их выполнение avg_user'у
CREATE OR REPLACE FUNCTION get_results(rating_begin_date DATE, rating_end_date DATE, discipline_length INT, discipline_style VARCHAR, rating_gender CHAR, rating_pool_length INT, min_age INT DEFAULT 0, max_age INT DEFAULT 100) 
RETURNS TABLE(rank_number BIGINT, surname VARCHAR, athlete_name VARCHAR, birth_year INT, rank VARCHAR, region_name VARCHAR, competition_title VARCHAR, city VARCHAR, time_result VARCHAR, points INT, result_date DATE) AS $$
BEGIN
    RETURN QUERY 
    SELECT ROW_NUMBER() OVER (ORDER BY res.points DESC) AS rank_number,
           s.surname,
           s.athlete_name,
           s.birth_year,
           s.rank,
           r.region_name,
           c.title AS competition_title,
           c.city,
           res.time_result,
           res.points,
           res.result_date
      FROM Result res
      JOIN Athlete s ON res.athlete_id = s.id_athlete
      JOIN Competition c ON res.competition_id = c.id_competition
      JOIN Region r ON s.code_region = r.region_code
      WHERE res.result_date BETWEEN rating_begin_date AND rating_end_date
        AND (EXTRACT(YEAR FROM CURRENT_DATE) - s.birth_year) BETWEEN min_age AND max_age
        AND s.gender = rating_gender
        AND c.pool_length = rating_pool_length
      ORDER BY res.points DESC;
END;
$$
 LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_athlete_results(
    p_surname VARCHAR,
    p_athlete_name VARCHAR,
    p_birth_year INT,
    p_rank VARCHAR,
    p_gender CHAR,
    p_code_region CHAR
) 
RETURNS TABLE (
    discipline_length INT,
    discipline_style VARCHAR,
    competition_title VARCHAR,
    pool_length INT,
    time_result VARCHAR,
    points INT,
    result_date DATE,
    place INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        r.discipline_length,
        r.discipline_style,
        c.title AS competition_title,
        c.pool_length,
        r.time_result,
        r.points,
        r.result_date,
        r.place
    FROM 
        Result r
    JOIN 
        Athlete a ON r.athlete_id = a.id_athlete
    JOIN 
        Competition c ON r.competition_id = c.id_competition
    WHERE 
        a.surname = p_surname AND
        a.athlete_name = p_athlete_name AND
        a.birth_year = p_birth_year AND
        a.rank = p_rank AND
        a.gender = p_gender AND
        a.code_region = p_code_region
    ORDER BY 
        r.result_date DESC;
END;
$$
 LANGUAGE plpgsql;

GRANT EXECUTE ON FUNCTION get_results(DATE, DATE, INT, VARCHAR, CHAR, INT, INT, INT) TO avg_user;
GRANT EXECUTE ON FUNCTION get_athlete_results(VARCHAR, VARCHAR, INT, VARCHAR, CHAR, CHAR) TO avg_user;
SELECT
    record_changelog.rec_ts,
    record_changelog.rec_territory,
    record_changelog.rec_category,
    record_changelog.rec_value

FROM
    record_changelog
    LEFT JOIN (
        SELECT
            rec_category,
            rec_territory,
            max(rec_value) AS previous_value
        FROM
            record_changelog
        GROUP BY
            rec_category,
            rec_territory
    ) AS history_log
      ON latest_daily_data.rec_territory = history_log.rec_territory
      AND latest_daily_data.rec_category = history_log.rec_category
      AND latest_daily_data.rec_value > history_log.rec_value

WHERE
    rec_category IN ('case', 'death')
    AND rec_territory = 'Trinidad and Tobago'
      latest_daily_data.rec_value > 0
  AND (latest_posts.rec_value IS NULL OR latest_posts.rec_value < latest_daily_data.rec_value)
  AND (latest_posts.rec_value IS NULL OR latest_posts.ts > current_timestamp - interval '1 hour')
  AND current_date = latest_daily_data.rec_dt

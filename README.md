# signal-chat-analysis


SQL query for message extraction

```
SELECT
    COALESCE(mms.body, mms.quote_body),
    rcp.profile_joined_name,
    DATETIME(ROUND(mms.date_received / 1000), 'unixepoch') AS "Date received"
FROM mms
LEFT JOIN thread ON thread._id = mms.thread_id
LEFT JOIN groups ON thread.thread_recipient_id = groups.recipient_id
LEFT JOIN
    (SELECT * FROM recipient WHERE recipient.group_id IS NULL) AS rcp
    ON rcp._id = mms.address OR (rcp._id = 1 AND mms.address = groups.recipient_id)
WHERE groups.title = '<group_name>'
ORDER BY date_received DESC
```

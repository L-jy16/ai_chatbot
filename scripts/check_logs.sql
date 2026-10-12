-- Read-only inspection for one user; never paste a password or API key here.
-- SQLite CLI usage:
--   sqlite3 -readonly chatbot.db
--   .headers on
--   .mode column
--   .parameter init
--   .parameter set :user_id 1
--   .parameter set :limit 20
--   .read scripts/check_logs.sql
-- Or use: python scripts/check_logs.py --db chatbot.db --user-id 1
SELECT id, user_id, mode, created_at, question, answer, status
FROM chats
WHERE user_id = :user_id
ORDER BY created_at DESC, id DESC
LIMIT :limit;

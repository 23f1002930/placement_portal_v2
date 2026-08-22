# Viva Questions and Short Answers

1. What problem is solved? Campus recruitment workflow coordination.
2. Why Flask? It is small, explicit, and suitable for REST APIs.
3. Why Vue 3? Reactive browser views with little boilerplate.
4. Why Bootstrap? Responsive, consistent UI components.
5. Why SQLite? Zero-setup local relational storage.
6. What is SQLAlchemy? An ORM mapping classes to relational tables.
7. What is an application factory? A function that constructs/configures Flask.
8. What is a blueprint? A grouped set of Flask routes.
9. What is REST? Resource-oriented HTTP endpoints and methods.
10. Why native fetch? It avoids an unnecessary HTTP dependency.
11. How is identity verified? Username/email plus a password hash check.
12. Are passwords stored? Only salted hashes are stored.
13. What does the session contain? User ID and role.
14. What is authorization? Checking permission after identity is known.
15. Why recheck the user? An inactive account must lose access immediately.
16. How is one admin enforced? There is no admin registration and initialization creates one only if absent.
17. How is ownership enforced? Queries include the signed-in company/student ID.
18. Why return 401? The caller is unauthenticated.
19. Why return 403? The caller is known but forbidden.
20. Why return 409? The request conflicts with current state.
21. What is a foreign key? A reference preserving relationships between tables.
22. What is the duplicate safeguard? A unique `(student_id, drive_id)` constraint.
23. Why also check duplicates in code? It gives a friendly error; the DB remains final protection.
24. How is eligibility calculated? Department, CGPA, and year comparisons.
25. Where is eligibility enforced? On the server; the UI is only guidance.
26. What is the drive lifecycle? Pending, approved/rejected, then optionally closed.
27. What is the application lifecycle? Applied, shortlisted, selected or rejected.
28. Why validate transitions? It prevents impossible workflow states.
29. How is a deadline checked? Against timezone-aware current UTC time.
30. How are files secured? Size limit, PDF extension, and secure filename.
31. What is pagination? Fetching a bounded page instead of all rows.
32. Why indexes? Faster filtering on frequently queried columns.
33. What is an N+1 query? One parent query followed by a query per child.
34. What is Redis used for? Cache plus Celery broker/result backend.
35. What is cache TTL? Automatic expiry duration of a cached value.
36. How do you change TTL? Set `CACHE_TTL`.
37. What if Redis fails? Cache calls safely fall back to database queries.
38. What is Celery? A distributed background task queue.
39. What is Celery beat? A periodic task scheduler.
40. What does the reminder task do? Creates notifications for imminent drives.
41. What does the report task do? Aggregates statuses into local HTML.
42. How does CSV export work? It writes selected application columns using Python `csv`.
43. How do you change CSV columns? Edit the header and row values in `export()`.
44. How is email disabled? Leave SMTP variables empty; local output still works.
45. How would you add a channel? Add a notification service invoked by tasks.
46. How would you add a role? Add role validation, a profile/model, routes, and UI navigation.
47. How would you change CGPA logic? Modify `drive_json` and matching apply validation.
48. How would you add a status? Update allowed transitions, badges, tests, and docs.
49. How would you modify the report? Change aggregations/templates in `monthly_report()`.
50. How are secrets managed? Environment variables and an ignored `.env` file.
51. What is audit logging? Recording important user actions and entity IDs.
52. How are API errors shaped? Consistent success false, message, and errors JSON.
53. Why test complete workflows? Unit success does not prove role integration.
54. How do you debug a failed route? Inspect status/JSON, logs, session, and database state.
55. How would you handle Celery failure? Keep the job queued/failed, notify, and allow retry.
56. How would you prevent SQL injection? Use ORM expressions, never concatenate raw SQL.
57. What is SameSite? Cookie control reducing cross-site request risk.
58. Why HttpOnly? Browser JavaScript cannot read the session cookie.
59. What is cache invalidation? Removing stale values after mutations.
60. What should a student understand before submission? Every model, route, rule, task, and UI call.

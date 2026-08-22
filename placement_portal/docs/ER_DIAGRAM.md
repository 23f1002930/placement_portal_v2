# ER Diagram

```mermaid
erDiagram
 USER ||--o| STUDENT : has
 USER ||--o| COMPANY : has
 USER ||--o{ NOTIFICATION : receives
 USER ||--o{ ACTIVITY_LOG : creates
 COMPANY ||--o{ PLACEMENT_DRIVE : owns
 STUDENT ||--o{ APPLICATION : submits
 PLACEMENT_DRIVE ||--o{ APPLICATION : receives
 STUDENT ||--o{ EXPORT_JOB : requests
```

A user has one role-specific profile. Companies own drives; students and drives meet through applications. A student-drive pair is unique. Notifications and logs reference users, while export jobs reference students.


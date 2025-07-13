create table events
(
    user_id    int,
    name       varchar,
    value      varchar,
    json_data  json,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

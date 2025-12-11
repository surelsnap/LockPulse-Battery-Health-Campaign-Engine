create table if not exists notification_campaigns (
    campaign_id varchar(64) primary key,
    run_date timestamp not null,
    title text not null,
    body text not null,
    lock_count integer not null
);

create table if not exists notification_events (
    id bigserial primary key,
    campaign_id varchar(64) not null references notification_campaigns(campaign_id) on delete cascade,
    event_type varchar(64) not null,
    lock_id varchar(128),
    user_id varchar(128),
    fcm_message_id varchar(256),
    event_time timestamp not null default now()
);

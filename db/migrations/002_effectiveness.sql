create table if not exists notification_effectiveness (
    campaign_id varchar(64) primary key references notification_campaigns(campaign_id) on delete cascade,
    targets integer not null,
    checked integer not null,
    rate numeric(5,2) not null,
    snapshot_time timestamp not null default now()
);

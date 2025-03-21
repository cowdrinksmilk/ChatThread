-- clean up existing tables
drop table if exists messages CASCADE;      -- messages go first because of foreign keys
drop table if exists suspensions CASCADE;   -- suspensions reference users and communities
drop table if exists users CASCADE;         -- users table is needed by most others
drop table if exists communities CASCADE;   -- communities are needed for channels
drop table if exists channels CASCADE;      -- channels handle group messaging
drop table if exists community_members CASCADE; -- tracks who’s in what community
drop table if exists mentions CASCADE;      -- stores @mentions in messages

-- user accounts
create table users (
    user_id serial primary key,             -- auto-incrementing id
    username varchar(20) not null unique,   -- unique username for @mentions
    email varchar(35) not null unique,      -- unique email for notifications
    first_name varchar(20) not null,        -- first name
    last_name varchar(20) not null,         -- last name
    user_password text not null,            -- hashed password for security
    created_at timestamp default current_timestamp not null,  -- account creation time
    last_username_change timestamp default current_timestamp not null  -- restricts name changes
);

-- communities (groups of users)
create table communities (
    community_id serial primary key,        -- auto-incrementing id
    name varchar(50) not null unique,       -- unique community name
    description text,                       -- optional description
    created_at timestamp default current_timestamp not null  -- when created
);

-- channels (chat rooms within communities)
create table channels (
    channel_id serial primary key,          -- auto-incrementing id
    community_id integer references communities(community_id) on delete CASCADE,  -- belongs to a community
    name varchar(50) not null,              -- channel name
    description text,                       -- optional description
    created_at timestamp default current_timestamp not null,  -- when created
    unique(community_id, name)              -- must be unique within the community
);

-- tracks who’s in what community
create table community_members (
    community_id integer references communities(community_id) on delete CASCADE,  -- community id
    user_id integer references users(user_id) on delete CASCADE,    -- user id
    joined_at timestamp default current_timestamp not null,         -- when they joined
    primary key (community_id, user_id)     -- no duplicate memberships
);

-- keeps track of suspensions
create table suspensions (
    suspension_id serial primary key,
    user_id integer references users(user_id) on delete CASCADE,     -- who’s suspended
    community_id integer references communities(community_id) on delete CASCADE,  -- where they’re suspended
    start_date timestamp not null,           -- suspension start time
    end_date timestamp not null,             -- suspension end time
    suspension_reason text,                  -- optional reason for suspension
    check (end_date > start_date)            -- makes sure dates make sense
);

-- messages (both direct and in channels)
create table messages (
    message_id serial primary key,           -- auto-incrementing id
    sender_id integer references users(user_id) on delete CASCADE,    -- who sent it
    receiver_id integer references users(user_id) on delete CASCADE,  -- who received it (if DM)
    channel_id integer references channels(channel_id) on delete CASCADE,  -- where it was sent (if channel)
    message_content text not null,           -- the actual message
    timestamp timestamp default current_timestamp not null,  -- when sent
    is_read boolean default false,           -- read/unread status
    is_direct_message boolean default false, -- distinguishes DM from channel messages
    check (                                  -- ensures correct message type
        (is_direct_message = true and receiver_id is not null and channel_id is null) or
        (is_direct_message = false and receiver_id is null and channel_id is not null)
    ),
    check (sender_id <> receiver_id)         -- no self-messaging
);

-- tracks @mentions in messages
create table mentions (
    mention_id serial primary key,
    message_id integer references messages(message_id) on delete CASCADE,  -- which message
    mentioned_user_id integer references users(user_id) on delete CASCADE, -- who was mentioned
    created_at timestamp default current_timestamp not null               -- when it happened
);

-- indexes for faster lookups
create index idx_messages_sender_receiver on messages (sender_id, receiver_id);  -- lookup DMs
create index idx_messages_channel on messages (channel_id);                      -- lookup channel messages
create index idx_suspensions_user_community on suspensions (user_id, community_id);  -- check suspensions
create index idx_users_username on users (username);                             -- find users by username
create index idx_community_members on community_members (community_id, user_id); -- find community members
create index idx_mentions_user on mentions (mentioned_user_id);                  -- lookup mentions

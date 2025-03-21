-- test data seeds for chat system

-- og users: comedy group
insert into users(username, email, first_name, last_name, user_password) values
('ab0tt', 'abott1@gmail.com', 'Abott', 'Hannah', 'password'),       -- abbott and costello duo
('costell0', 'cost3llo@gmail.com', 'Costello', 'Lee', 'password'),  -- comedy partner
('m03', 'mo3bamba@gmail.com', 'Moe', 'Charles', 'password'),        -- three stooges members
('l@rry', 'larry1@gmail.com', 'Larry', 'Byrd', 'password'),         -- currently suspended
('curl33', 'curl33@gmail.com', 'Curly', 'Chan', 'password'),        -- suspended in 90s
('DrMarvin', 'drmarvin@gmail.com', 'Leo', 'Marvin', 'password'),    -- what about bob reference
('Bob', 'bob@gmail.com', 'Bob', 'Johnson', 'password');             -- for username tests


-- dune users
insert into users(username, email, first_name, last_name, user_password) values
('spicelover', 'spice@dune.com', 'Spice', 'Melange', 'password'),   -- arrakis member
('Paul', 'paul@dune.com', 'Paul', 'Atreides', 'password');          -- for messaging tests

-- community set up
insert into communities(name, description) values
('Arrakis', 'The desert planet community'),    -- dune themed
('Comedy', 'For all things comedy'),           -- for main users
('TestCom', 'Test community');                 -- testing purposes

-- community channels
insert into channels(community_id, name, description) values
((select community_id from communities where name = 'Arrakis'), 'Worms', 'Discussion about sandworms'),
((select community_id from communities where name = 'Comedy'), 'ArgumentClinic', 'No it isn''t'),
((select community_id from communities where name = 'TestCom'), 'TestChannel', 'Testing channel');

-- add comedy members
insert into community_members(community_id, user_id)
select c.community_id, u.user_id
from communities c, users u
where c.name = 'Comedy' and u.username in ('ab0tt', 'costell0', 'm03', 'l@rry', 'curl33');

-- add arrakis members
insert into community_members(community_id, user_id)
select c.community_id, u.user_id
from communities c, users u
where c.name = 'Arrakis' and u.username in ('Paul', 'spicelover');

-- historic messages
insert into messages(sender_id, receiver_id, message_content, timestamp, is_read, is_direct_message) values
((select user_id from users where username = 'ab0tt'),
 (select user_id from users where username = 'costell0'),
'Hello Costello!', '1950-01-01 10:00:00', false, true),
((select user_id from users where username = 'costell0'),
 (select user_id from users where username = 'ab0tt'),
'Hello Abbott!', '1950-01-01 10:05:00', true, true);

-- test messages between paul and moe
insert into messages (sender_id, receiver_id, message_content, timestamp, is_read, is_direct_message) values
((select user_id from users where username = 'Paul'),
 (select user_id from users where username = 'm03'),
'First test message', '2024-01-01 10:00:00', false, true),
((select user_id from users where username = 'm03'),
 (select user_id from users where username = 'Paul'),
'Second test message', '2024-01-01 10:01:00', false, true);

-- community suspensions
insert into suspensions(user_id, community_id, start_date, end_date) values
((select user_id from users where username = 'l@rry'),              -- larry suspended from comedy
 (select community_id from communities where name = 'Comedy'),
'2010-01-01', '2060-01-01'),
((select user_id from users where username = 'curl33'),             -- curly's past suspension
 (select community_id from communities where name = 'Comedy'),
'1990-01-14', '1999-09-10');

-- global suspension
insert into suspensions(user_id, start_date, end_date) values
((select user_id from users where username = 'l@rry'),              -- larry globally suspended
'2010-01-01', '2060-01-01');

-- db 4
insert into messages(sender_id, receiver_id, message_content, timestamp, is_read, is_direct_message) values
((select user_id from users where username = 'ab0tt'),
 (select user_id from users where username = 'costell0'),
'please reply', '1953-09-23 10:00:00', false, true),
((select user_id from users where username = 'costell0'),
 (select user_id from users where username = 'ab0tt'),
'i replied already!', '1953-09-23 10:05:00', false, true);
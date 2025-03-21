# my plans for improving the chat system

i want to add a feature of reactions so that users should be able to react to messages with emojis or gifs.

### adding reactions

i need to make a reasctions storage table
```sql
create table reactions (
    reaction_id serial primary key,
    message_id integer references messages(message_id),
    user_id integer references users(user_id),
    reaction_type text not null,
    created_at timestamp default current_timestamp
);
```

i'll need these api methods:
- add_reaction() so people can add reactions to messages 
- remove_reaction() to take them away
- get_message_reactions() to see who reacted with what

als have to update get_messages() to show reactions with the messages

  

threads would be cool to have too. gonna need to update the messages table:
```sql
alter table messages add column parent_message_id integer references messages(message_id);
alter table messages add column thread_id integer;
alter table messages add column reply_count integer default 0;
```

for the api i'll need:
- reply_to_message() for adding replies
- get_thread_messages() to see a whole thread
- get_user_threads() to find your conversations

### other stuff to change

- need to make message queries work with threads
- track which thread messages belong to
- count unread messages in threads
- make search work with threaded messages too
yhis will voer more cases
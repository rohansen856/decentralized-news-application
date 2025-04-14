// MongoDB Initialization Script
// This script creates the application database and a user for it

// Switch to the admin database
db = db.getSiblingDB('admin');

// Create application database
db = db.getSiblingDB('news_app');

// Create a user for the news_app database
db.createUser({
  user: 'news_user',
  pwd: 'news_password',
  roles: [
    {
      role: 'readWrite',
      db: 'news_app'
    }
  ]
});

print('MongoDB initialization completed successfully!');